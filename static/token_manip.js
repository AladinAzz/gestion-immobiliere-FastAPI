// After receiving the JWT from the server



export function saveToken(jwtToken) {
    localStorage.setItem('access_token', jwtToken);
  }
  
  // Call the login endpoint
  
  
  export function getToken() {
    return localStorage.getItem('access_token');
  }
  
  // Example of using the token for an API request
  export async function getUserData() {
    const token = getToken();
    const response = await fetch('/protected-endpoint', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`, // Include the token in the Authorization header
      },
    });
  
    if (response.ok) {
      const data = await response.json();
      console.log(data);
    } else {
      alert('Unauthorized');
    }
  }
  

 



export function clearToken() {
    localStorage.removeItem('access_token');
    alert('You have logged out');
  }
  


  export function postRedirect(url,data) {
    // Create a form element
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = url;
  
    // Add the data to the form as hidden input fields
    for (const key in data) {
      if (data.hasOwnProperty(key)) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = data[key];
        form.appendChild(input);
      }
    }
  
    // Append the form to the body
    document.body.appendChild(form);
  
    // Submit the form
    form.submit();
  }
  
  
  
  
  
  
  
  