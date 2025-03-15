import { useMemo, useRef, useState } from "react";
import Transition from "@/components/Transition";
import ImportIcon from "@/lib/assets/import.svg"
import CloseIcon from "@/lib/assets/close.svg"
import { useNavigate } from "react-router-dom";
import { useShallow } from "zustand/react/shallow";
import { useCallback } from "react";
import useStore from "@/lib/store";
import { useTranslation } from 'react-i18next';


const getModel = (orientation) => {
    return `/model/${orientation}.png`
}

const getSample = (id, orientation) => {
    return `/sample/${id}/${orientation}.jpg`
}


const UploadFactory = ({ orientation = "f", next = "/claim/upload/2", ...props }) => {
    const [scope, photos, setPhoto] = useStore(useShallow((state) => [state.scope, state.photos, state.setPhoto]))

    const [usingSample, setUsingSample] = useState(false);

    const photoDebounce = useRef(null)

    const { t } = useTranslation();

    const id = useMemo(() => scope?.policyId ?? "", [scope]);

    const sample = useMemo(() => id ? getSample(id, orientation) : null, [id])

    const model = useMemo(() => getModel(orientation) ?? null, [id])

    const photo = photos[orientation]

    const navigate = useNavigate();

    const ref = useRef();

    const handleFileChange = useCallback((e) => {
        const selectedFiles = e.target.files;
        if (!selectedFiles?.length) return;

        const newFile = selectedFiles[0];
        setPhoto(orientation, newFile);
        photoDebounce.current = newFile
    }, [setPhoto])

    const uploadSample = useCallback(async () => {
        // Programtically upload associated sample file
        setUsingSample(true)
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
    }, [scope, setUsingSample])

    const clear = (e) => {
        e.preventDefault()
        if (ref.current) {
            ref.current.value = '';
            setPhoto(orientation, null)
            setUsingSample(false)
        }
    }

    return (
        <>
            <Transition>
                <div className="flex justify-center ">
                    <div>
                        <h1 className="text-3xl text-center ">
                            {t(`upload.${orientation}.title`)}
                        </h1>
                        <p className="text-muted-foreground mt-2">
                            {t(`upload.${orientation}.description`)}
                        </p>

                        <img src={model} className="dark:invert opacity-50 h-[85px] xs:h-[110px] mx-auto mt-12 select-none" alt="car model" />
                    </div>
                </div>
                <div className="flex justify-center mt-16 ">

                    <input
                        ref={ref}
                        type="file"
                        id="file"
                        hidden
                        name="file"
                        accept=".png,.jpg,.jpeg" // TODO: pdf no work good
                        onChange={handleFileChange}
                    />
                    <label htmlFor="file" className="relative max-w-[500px] w-full h-[300px] border border-dashed rounded-md flex flex-col gap-y-2 items-center justify-center text-muted-foreground cursor-pointer">
                        <ImportIcon />

                        <button data-file={!!photo} className="absolute top-0 right-0 data-[file=true]:opacity-100 opacity-0 transition-opacity flex items-center p-4 " onClick={clear}>
                            <CloseIcon />
                        </button>

                        <img data-file={!!photo} src={usingSample ? sample : photoDebounce.current ? URL.createObjectURL(photoDebounce.current) : null} alt="uploaded photo" className="absolute h-[200px] rounded-lg mx-auto my-auto data-[file=true]:opacity-100 opacity-0 transition-opacity" />

                    </label>

                </div>

                <div className="flex flex-col ">
                    <button className="disabled:opacity-20 text-center py-12 text-muted-foreground text-sm hover:text-foreground disabled:text-muted-foreground disabled:cursor-not-allowed transition-colors cursor-pointer select-none" onClick={uploadSample} disabled={!!photo}>

                        {t('upload.btn.useSample')}

                    </button>
                </div>


                <div className="h-24" />


            </Transition>
            <div className="fixed top-0 left-0 w-screen h-screen pointer-events-none">


                <footer className="absolute bottom-0 left-0 bg-background w-full flex justify-center items-center h-24 border-t pointer-events-auto">


                    <button disabled={!photo} className="btn mb-1"
                        onClick={() => navigate(next, { scroll: false })}>
                        {t('btn.next')}
                    </button>



                </footer>
            </div>
        </>
    )
}

export default UploadFactory;