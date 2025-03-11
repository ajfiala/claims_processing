const BACKEND_URL = "https://api.bangkok.solutions";

const headers = {
    'Content-Type': 'application/json',
};

export const getForm = async (description) => {
    const response = await fetch(`${BACKEND_URL}/api/form`, {
        method: 'POST',
        headers,
        credentials: 'include',
        body: JSON.stringify({
            description
        }),
    });
    
    const json = await response.json();
    if (!response.ok) {
        throw new Error(json?.detail ?? 'Network response was not ok');
    }
    
    return json;
};

export const getFormWithImage = async (description, imageFile) => {
    const formData = new FormData();
    formData.append('description', description);
    
    if (imageFile) {
        formData.append('image', imageFile);
    }
    
    const response = await fetch(`${BACKEND_URL}/api/form-with-image`, {
        method: 'POST',
        credentials: 'include',
        // Don't set Content-Type header - FormData will set it with boundary
        body: formData,
    });
    
    const json = await response.json();
    if (!response.ok) {
        throw new Error(json?.detail ?? 'Network response was not ok');
    }
    
    return json;
};