import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import useStore from "@/lib/store";
import { useShallow } from "zustand/react/shallow";
import Transition from "../components/Transition";
import { Textarea } from "@/components/shadcn/textarea";
import { Button } from "@/components/shadcn/button";
import { Camera, X } from 'lucide-react';

const Describe = () => {
    const [description, setDescription] = useStore(useShallow(state => [state.description, state.setDescription]));
    const setImageFile = useStore(state => state.setImageFile);
    const navigate = useNavigate();
    
    const fileInputRef = useRef(null);
    const [imageSrc, setImageSrc] = useState(null);
    
    const handleFileInputChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        if (!file.type.match('image.*')) {
            // Could add a toast notification here
            console.error('Please upload an image file');
            return;
        }
        
        setImageFile(file);
        
        // Create a preview
        const reader = new FileReader();
        reader.onload = (e) => setImageSrc(e.target.result);
        reader.readAsDataURL(file);
    };
    
    const triggerFileInput = () => {
        fileInputRef.current?.click();
    };
    
    const removeImage = () => {
        setImageFile(null);
        setImageSrc(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };
    
    return (
        <Transition>
            <div className="flex justify-center">
                <div>
                    <h1 className="text-3xl text-center">
                        Please describe what happened.
                    </h1>
                </div>
            </div>
            
            <div className="px-4 flex flex-col items-center w-full mt-16">
                <Textarea 
                    placeholder="e.g: My car got stolen at Arby's while I went in to get ice cream" 
                    className="w-full sm:w-[600px] shadow-2xl min-h-[200px] border-[rgba(236,236,236,0.43)] dark:border"
                    value={description} 
                    onChange={e => setDescription(e.target.value)}
                />
                
                <div className="w-full sm:w-[600px] mt-8">
                    <p className="text-sm font-medium mb-2 text-muted-foreground">Photo (optional)</p>
                    
                    {!imageSrc ? (
                        <div 
                            className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg p-6 bg-gray-50 hover:bg-gray-100 cursor-pointer transition-colors" 
                            onClick={triggerFileInput}
                        >
                            <Camera className="h-10 w-10 text-gray-400 mb-2" />
                            <p className="text-sm text-gray-500">Click to upload an image</p>
                            <p className="text-xs text-gray-400 mt-1">JPEG, PNG, GIF up to 10MB</p>
                        </div>
                    ) : (
                        <div className="relative rounded-lg overflow-hidden border border-gray-200">
                            <img 
                                src={imageSrc} 
                                alt="Preview" 
                                className="w-full object-cover max-h-64"
                            />
                            <button 
                                type="button"
                                onClick={removeImage}
                                className="absolute top-2 right-2 bg-black bg-opacity-50 rounded-full p-1 hover:bg-opacity-70 transition-colors"
                            >
                                <X className="h-5 w-5 text-white" />
                            </button>
                        </div>
                    )}
                    
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileInputChange}
                        accept="image/*"
                        className="hidden"
                    />
                </div>
            </div>
            
            <div className="w-full flex justify-center mt-16">
                <button 
                    disabled={!description} 
                    className="btn" 
                    onClick={() => navigate("/claim/form")}
                >
                    Next
                </button>
            </div>
        </Transition>
    );
};

export default Describe;