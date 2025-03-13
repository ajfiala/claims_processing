const BACKEND_URL = import.meta.env.VITE_BACKEND_URL //api.bangkok.solutions



export const analyzeImages = async (namedInsured, make, model, f, fl, l, bl, b, br, r, fr) => {
    const body = new FormData();

    body.append("front", f);
    body.append("front_left", fl);
    body.append("left", l);
    body.append("back_left", bl);
    body.append("back", b);
    body.append("back_right", br);
    body.append("right", r);
    body.append("front_right", fr);

    body.append("insured_name", namedInsured);
    body.append("vehicle_make", make);
    body.append("vehicle_model", model);

    const res = await fetch(`${BACKEND_URL}/analyze-images`, {
        method: 'POST',
        body
    })

    const json = await res.json();
    if (!res.ok) {
        throw new Error(json?.detail ?? 'Network response was not ok')
    }

    return json
}