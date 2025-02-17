const BACKEND_URL = import.meta.env.VITE_BACKEND_URL

console.log(BACKEND_URL)

const headers = {
    'Content-Type': 'application/json',
}

export const getForm = async (description) => {
    const response = await fetch(`${BACKEND_URL}/form`, {
        method: 'POST',
        headers,
        credentials: 'include',
        body: JSON.stringify({
            description
        }),
    })
    const json = await response.json();
    if (!response.ok) {
        throw new Error(json?.detail ?? 'Network response was not ok')
    }
    return json
}