// This is a wrapper around the Python function to make it work with Netlify Functions
const { spawn } = require('child_process');
const path = require('path');

exports.handler = async function(event, context) {
  try {
    // Prepare the Lambda event to pass to Python
    const args = [
      path.join(__dirname, 'app.py'),
      JSON.stringify(event),
      JSON.stringify(context)
    ];

    // Spawn Python process to execute our Flask app
    const python = spawn('python', args);
    
    // Collect stdout and stderr
    let stdoutData = '';
    let stderrData = '';
    
    python.stdout.on('data', data => {
      stdoutData += data;
    });
    
    python.stderr.on('data', data => {
      stderrData += data;
    });
    
    // Wait for the process to complete
    await new Promise((resolve, reject) => {
      python.on('close', code => {
        if (code !== 0) {
          reject(new Error(`Python process exited with code ${code}`));
        } else {
          resolve();
        }
      });
    });
    
    // If there was error output, log it
    if (stderrData) {
      console.error('Python stderr:', stderrData);
    }
    
    // Parse and return the response from Python
    const response = JSON.parse(stdoutData);
    return {
      statusCode: response.statusCode || 200,
      headers: response.headers || { 'Content-Type': 'text/html' },
      body: response.body || ''
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal Server Error' })
    };
  }
}; 