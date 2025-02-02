from flask import Flask, request, render_template, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
from requests.exceptions import RequestException
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
import markdown


load_dotenv()

MAX_RETRIES = 3
RETRY_DELAY = 2  

def initialize_gemini():
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    if not api_key.startswith('AIza'):
        raise ValueError("Invalid API key format. Please check your API key in .env file")
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-pro')
        # Test the API key with a simple prompt
        response = model.generate_content("test")
        return model
    except Exception as e:
        logger.error(f"Failed to initialize Gemini: {str(e)}")
        if "API_KEY_INVALID" in str(e):
            raise ValueError("Invalid API key. Please get a new API key from Google AI Studio")
        raise

def generate_with_retry(model, prompt):
    for attempt in range(MAX_RETRIES):
        try:
            return model.generate_content(prompt)
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                raise

app = Flask(__name__)
try:
    model = initialize_gemini()
except Exception as e:
    logger.error(f"Failed to initialize Gemini: {str(e)}")
    model = None

def create_code_prompt(params):
    """Create a structured prompt for code generation"""
    prompt = f"""
    Please generate code based on the following requirements:
    
    Language: {params.get('language', 'Python')}
    Include error handling: {params.get('error_handling', False)}
    
    Task Description: {params.get('description', '')}
    
    Requirements:
    1. Generate code in {params.get('language', 'Python')}
    2. {' Include error handling and try-catch blocks' if params.get('error_handling') else 'Basic implementation without error handling'}
    3. Include clear comments and documentation
    4. Follow {params.get('language', 'Python')} best practices
    
    Please format the response with markdown code blocks using the appropriate language tag.
    """
    return prompt

def format_code_response(response_text):
    """Format the code response with syntax highlighting"""
    try:
        # Parse the response to separate code and explanation
        sections = response_text.split('```')
        formatted_sections = []
        
        for i, section in enumerate(sections):
            if i % 2 == 0:  # This is explanation text
                formatted_sections.append(markdown.markdown(section))
            else:  # This is code
                # Extract language if specified
                code_lines = section.split('\n')
                if code_lines[0]:
                    language = code_lines[0]
                    code = '\n'.join(code_lines[1:])
                else:
                    language = 'python'
                    code = section
                    
                try:
                    lexer = get_lexer_by_name(language.lower())
                    formatted_code = highlight(
                        code,
                        lexer,
                        HtmlFormatter(style='monokai', cssclass='codehilite')
                    )
                    formatted_sections.append(formatted_code)
                except:
                    formatted_sections.append(f'<pre><code>{code}</code></pre>')
        
        return ''.join(formatted_sections)
    except Exception as e:
        return f"Error formatting response: {str(e)}"

def process_editor_command(command, code, line_number=None):
    """Process editor commands for pattern matching and replacements"""
    try:
        if 'change' in command or 'replace' in command:
            # Extract the "from" and "to" words
            words = command.lower().split()
            try:
                from_idx = words.index('change') + 1
                to_idx = words.index('to') + 1
                from_word = words[from_idx]
                to_word = words[to_idx]
            except (ValueError, IndexError):
                return code, "Invalid command format. Use 'change [word] to [new_word]'"

            if line_number is not None:
                # Change word only in specific line
                lines = code.split('\n')
                if 0 <= line_number < len(lines):
                    lines[line_number] = lines[line_number].replace(from_word, to_word)
                    return '\n'.join(lines), f"Changed '{from_word}' to '{to_word}' in line {line_number + 1}"
                return code, f"Line number {line_number + 1} is out of range"
            else:
                # Change word in entire code
                return code.replace(from_word, to_word), f"Changed all occurrences of '{from_word}' to '{to_word}'"

        return code, "No changes made"
    except Exception as e:
        return code, f"Error processing command: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/edit_code', methods=['POST'])
def edit_code():
    try:
        data = request.json
        command = data.get('command', '').lower()
        code = data.get('code', '')
        line_number = data.get('line_number')

        if 'go to line' in command:
            try:
                line_num = int(''.join(filter(str.isdigit, command))) - 1
                return jsonify({
                    'action': 'goto',
                    'line': line_num,
                    'status': 'success'
                })
            except ValueError:
                return jsonify({
                    'error': 'Invalid line number',
                    'status': 'error'
                })

        updated_code, message = process_editor_command(command, code, line_number)
        
        return jsonify({
            'code': updated_code,
            'message': message,
            'status': 'success'
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        })

@app.route('/generate', methods=['POST'])
def generate():
    try:
        if not model:
            return jsonify({
                'error': 'Gemini API not properly initialized.'
            }), 503

        data = request.json
        
        # Create structured prompt based on parameters
        prompt_params = {
            'language': data.get('language', 'Python'),
            'error_handling': data.get('error_handling', False),
            'description': data.get('prompt', '')
        }
        
        if not prompt_params['description']:
            return jsonify({'error': 'No prompt provided'}), 400

        prompt = create_code_prompt(prompt_params)

        try:
            response = generate_with_retry(model, prompt)
            formatted_response = format_code_response(response.text)
            
            return jsonify({
                'response': formatted_response,
                'raw_response': response.text,
                'status': 'success'
            })
        
        except Exception as e:
            return jsonify({
                'error': f'Failed to generate response: {str(e)}.',
                'status': 'error'
            }), 503
    
    except Exception as e:
        return jsonify({
            'error': 'An unexpected error occurred.',
            'status': 'error'
        }), 500

# Add health check endpoint
@app.route('/health')
def health_check():
    try:
        # Simple test prompt to verify API connection
        response = generate_with_retry(model, "test")
        return jsonify({'status': 'healthy', 'api_connection': 'ok'})
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'api_connection': 'failed'
        }), 503

if __name__ == '__main__':
    app.run(debug=True) 