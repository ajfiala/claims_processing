import { useMemo, useRef } from "react";
import Transition from "@/components/Transition";
import ImportIcon from "@/lib/assets/import.svg"
import CloseIcon from "@/lib/assets/close.svg"
import { useNavigate } from "react-router-dom";
import { useShallow } from "zustand/react/shallow";
import { useCallback } from "react";
import useStore from "@/lib/store";


const getModel = (orientation) => {
    return `/model/${orientation}.png`
}

const getSample = (id, orientation) => {
    return `/sample/${id}/${orientation}.jpg`
}


const UploadFactory = ({title="Upload Front Photo", description="Please take 3 steps back and take a photo of the Front bumper", orientation="f", next="/claim/upload/2", ...props}) => {
    const [scope, photos, setPhoto] = useStore(useShallow((state) => [state.scope, state.photos, state.setPhoto]))

    const id = useMemo(() => scope?.carId ?? "", [scope]);

    const sample = useMemo(() => id  ? getSample(id, orientation) : null, [id])

    const model = useMemo(() => getModel(orientation) ?? null, [id]) 

    const photo = photos[orientation]

    const navigate = useNavigate();

    const ref = useRef();

    const handleFileChange = useCallback((e) => {
        const selectedFiles = e.target.files;
        if (!selectedFiles?.length) return;

        const newFile = selectedFiles[0];
        setPhoto(orientation, newFile);
    }, [setPhoto])

    const uploadSample = useCallback(async () => {
        // Programtically upload associated sample file
        if (ref.current) {
            const res = await fetch(sample);
            if (!res.ok) {
              console.error(`Failed to fetch file: ${res.statusText}`);
              return
            }
            const blob = await res.blob();

            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(new File([blob], sample.split('/').pop() || 'downloaded-file', { type: blob.type }));
            ref.current.files = dataTransfer.files;
            ref.current.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }, [scope])

    const clear = (e) =>{
        e.preventDefault()
        if (ref.current) {
            ref.current.value = '';
            setPhoto(orientation, null)
        }
    }

    return (
        <Transition>
            <div className="flex justify-center ">
                <div>
                    <h1 className="text-3xl text-center ">
                        {title}
                    </h1>
                    <p className="text-muted-foreground mt-2">
                        {description}
                    </p>

                    <img src={model} className="dark:invert opacity-50 w-[300px] mx-auto mt-12 select-none" alt="car model"/>
                </div>
            </div>
            <div className="flex justify-center mt-24 ">

                <input
                    ref={ref}
                    type="file"
                    id="file"
                    hidden
                    name="file"
                    accept=".pdf,.png" // TODO: pdf no work good
                    onChange={handleFileChange}
                />
                <label htmlFor="file" className="relative max-w-[500px] w-full h-[300px] border border-dashed rounded-md flex flex-col gap-y-2 items-center justify-center text-muted-foreground cursor-pointer">
                    <ImportIcon />
                    <p data-file={!!photo} className="text-sm h-[20px] data-[file=true]:opacity-100 opacity-0 transition-opacity">
                        {photo?.name ?? ""}
                    </p>
                    <CloseIcon data-file={!!photo} className="absolute top-3 right-3 data-[file=true]:opacity-100 opacity-0 transition-opacity" onClick={clear}/>
                    <img data-file={!!photo} src={sample} alt="sample photo" className="absolute h-[200px] rounded-lg mx-auto my-auto data-[file=true]:opacity-100 opacity-0 transition-opacity"/>
                </label>

            </div>
            <div className="w-full flex justify-center pt-16 pb-6">
                <div className="flex flex-col">

                    <p className="text-center mb-12 text-muted-foreground text-sm hover:text-foreground transition-colors cursor-pointer select-none" onClick={uploadSample}>
                        or Use Sample File 
                    </p>


                    <button disabled={!photo} className="btn"
                        onClick={() => navigate(next)}>
                        Next
                    </button>


                </div>
            </div>
        </Transition>
    )
}

export default UploadFactory;