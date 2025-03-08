import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getFormWithImage } from '../lib/api';
import { ClaimContent, Container } from './components';
import { Button, Spinner, TextArea } from '../components/ui';
import { useToast } from '../hooks/useToast';
import { Camera, X } from 'lucide-react';

const DescribeWithImage = () => {
    const navigate = useNavigate();
    const { addToast } = useToast();
    const fileInputRef = useRef(null);
    
    const [description, setDescription] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [imageFile, setImageFile] = useState(null);
    const [imageSrc, setImageSrc] = useState(null);
    
    const handleFileInputChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        if (!file.type.match('image.*')) {
            addToast({
                title: 'Invalid file type',
                description: 'Please upload an image file',
                type: 'error'
            });
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
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!description.trim()) {
            addToast({
                title: 'Description required',
                description: 'Please provide a description of the incident',
                type: 'error'
            });
            return;
        }
        
        setIsLoading(true);
        
        try {
            const data = await getFormWithImage(description, imageFile);
            
            // Store the results in localStorage or context
            localStorage.setItem('formData', JSON.stringify(data));
            
            // Navigate to the form page
            navigate('/claim/form');
        } catch (error) {
            console.error('Error submitting form:', error);
            addToast({
                title: 'Error processing claim',
                description: error.message || 'Something went wrong. Please try again.',
                type: 'error'
            });
        } finally {
            setIsLoading(false);
        }
    };
    
    return (
        <motion.div
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            transition={{ duration: 0.3 }}
        >
            <Container>
                <ClaimContent
                    title="Describe your incident"
                    description="Please provide details about what happened. You can also upload a photo of the damage."
                >
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <TextArea
                            label="Description"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="Tell us what happened..."
                            rows={5}
                            required
                        />
                        
                        <div className="mt-4">
                            <p className="text-sm font-medium mb-2">Photo (optional)</p>
                            
                            {!imageSrc ? (
                                <div className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg p-6 bg-gray-50 hover:bg-gray-100 cursor-pointer transition-colors" onClick={triggerFileInput}>
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
                        
                        <div className="flex justify-end space-x-4 pt-4">
                            <Button
                                type="button"
                                variant="outline"
                                onClick={() => navigate('/')}
                                disabled={isLoading}
                            >
                                Back
                            </Button>
                            <Button
                                type="submit"
                                disabled={isLoading || !description.trim()}
                            >
                                {isLoading ? <Spinner className="mr-2" /> : null}
                                {isLoading ? 'Processing...' : 'Continue'}
                            </Button>
                        </div>
                    </form>
                </ClaimContent>
            </Container>
        </motion.div>
    );
};

export default DescribeWithImage;