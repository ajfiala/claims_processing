import { useShallow } from "zustand/react/shallow";
import useStore from "@/lib/store";
import { motion, AnimatePresence } from "framer-motion";
import Transition from "@/components/Transition";
import { useMemo, useState, useEffect } from "react";
import SuccessIcon from "@/lib/assets/success.svg"
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import { useTranslation } from 'react-i18next';

const DamageImage = ({ src, alt }) => {
    const [imageLoaded, setImageLoaded] = useState(false);
    const [error, setError] = useState(false);
    const [retryWithAlternate, setRetryWithAlternate] = useState(false);
    const angle = alt?.toLowerCase().replace(" damage", "").replace(" ", "_");

    const imageUrl = useMemo(() => {
        if (retryWithAlternate) {
            const photos = window.store?.getState()?.photos;
            const storeKey = {
                front: "f",
                front_left: "fl",
                front_right: "fr",
                left: "l",
                right: "r",
                back: "b",
                back_left: "bl",
                back_right: "br",
            }[angle];
            if (photos && storeKey && photos[storeKey] instanceof File) {
                return URL.createObjectURL(photos[storeKey]);
            }
            const policyId = window.store?.getState()?.scope?.policyId;
            return policyId ? `/sample/${policyId}/${storeKey}.jpg` : null;
        }
        return src;
    }, [src, angle, retryWithAlternate]);

    const handleError = () => {
        if (!retryWithAlternate) {
            setRetryWithAlternate(true);
            setError(false);
        } else {
            setError(true);
        }
    };

    if (error || !imageUrl) {
        return (
            <div className="p-6 rounded border bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-100 my-4 text-center">
                Image could not be loaded
                <p className="text-sm mt-2">{alt}</p>
            </div>
        );
    }

    return (
        <div className="my-4 text-center">
            <img
                src={imageUrl}
                alt={alt || "Vehicle damage"}
                onLoad={() => setImageLoaded(true)}
                onError={handleError}
                className={`max-w-full rounded-md border shadow-md max-h-64 mx-auto transition-opacity duration-300 ${imageLoaded ? "opacity-100" : "opacity-0"
                    }`}
            />
            <p className="text-sm text-gray-600 dark:text-gray-300 mt-2">{alt}</p>
        </div>
    );
};

const markdownComponents = {
    h1: ({ node, ...props }) => (
        <h1 className="text-2xl font-bold mb-2 border-b border-gray-300 dark:border-gray-700 pb-2 text-gray-900 dark:text-gray-100" {...props} />
    ),
    h2: ({ node, ...props }) => (
        <h2 className="text-xl font-semibold mt-6 mb-3 border-b border-gray-300 dark:border-gray-700 pb-1 text-gray-900 dark:text-gray-100" {...props} />
    ),
    p: ({ node, ...props }) => (
        <p className="my-2 text-gray-800 dark:text-gray-200 leading-relaxed" {...props} />
    ),
    strong: ({ node, ...props }) => (
        <strong className="font-semibold text-gray-900 dark:text-gray-100" {...props} />
    ),
    em: ({ node, ...props }) => (
        <em className="italic text-gray-800 dark:text-gray-200" {...props} />
    ),
    hr: () => <hr className="my-4 border-t border-gray-300 dark:border-gray-700" />,
    li: ({ node, ...props }) => <li className="ml-4 my-1 text-gray-800 dark:text-gray-200" {...props} />,
    ul: ({ node, ...props }) => <ul className="my-2" {...props} />,
    ol: ({ node, ...props }) => <ol className="my-2 list-decimal ml-4" {...props} />,
    img: ({ node, ...props }) => <DamageImage {...props} />,
};

const animate = {
    initial: { opacity: 0.01 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { type: "spring", stiffness: 100, damping: 20 },
};

const angleToFilename = {
    front: "front.jpg",
    front_left: "front-left.jpg",
    front_right: "front-right.jpg",
    left: "left.jpg",
    right: "right.jpg",
    back: "back.jpg",
    back_left: "back-left.jpg",
    back_right: "back-right.jpg",
};

const processMarkdown = (markdown) => {
    if (!markdown) return "";
    return markdown.replace(
        /!\[(.*?)\]\((image_placeholder_for_(.*?))\)/g,
        (match, alt, placeholder, angle) => {
            const filename = angleToFilename[angle] || `${angle.replace("_", "-")}.jpg`;
            return `![${alt}](/analyze-images/${filename})`;
        }
    );
};

const Results = () => {
    const [results, analyze, isThinking, scope, photos, reset] = useStore(
        useShallow((state) => [state.results, state.analyze, state.isThinking, state.scope, state.photos, state.reset])
    );
    const isSuccess = useMemo(() => !!results, [results]);
    const processedResults = useMemo(() => processMarkdown(results), [results]);
    const navigate = useNavigate();

    const { t } = useTranslation();

    

    useEffect(() => {
        window.store = { getState: () => ({ scope, photos }) };
        return () => {
            delete window.store;
        };
    }, [scope, photos]);

    useEffect(() => {
        analyze();
    }, []);

    return (
        <Transition>
            <AnimatePresence mode="sync">
                {isThinking ? (
                    <motion.div key="thinking" {...animate} className="absolute w-full">
                        <div className="flex justify-center">
                            <div>
                                <h1 className="text-3xl text-center text-gray-800 dark:text-gray-100">{t('results.loading')}</h1>
                            </div>
                        </div>
                        <div className="px-4 flex justify-center w-full mt-12" {...animate}>
                            <img src="/file-load.gif" className="w-[175px]" alt="file load" />
                        </div>
                    </motion.div>
                ) : (
                    <motion.div key="not-thinking" className="absolute w-full pb-12" {...animate}>
                        <div className="flex justify-center px-2">
                            <div>
                                <h1 className="text-3xl text-center text-gray-800 dark:text-gray-100">
                                    {t(`results.${isSuccess ? "success" : "error"}.title`)}
                                </h1>
                                <p className="mt-2 text-center text-gray-600 dark:text-gray-300">
                                    {t(`results.${isSuccess ? "success" : "error"}.description`)}
                                </p>
                            </div>
                        </div>
                        <div className="flex justify-center my-8">
                            <div className="flex flex-col items-center">
                                {!isSuccess ? (
                                    <>{t('results.error.message')}</>
                                ) : (
                                    <>
                                        <SuccessIcon className="text-[limegreen] w-full max-w-[120px] mb-6 mt-4" />
                                        <div className="sm:px-6 py-12 rounded-md sm:shadow-2xl max-w-3xl w-full my-6 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700">
                                            <ReactMarkdown components={markdownComponents}>{processedResults}</ReactMarkdown>
                                        </div>
                                        <button
                                            className="btn btn-secondary px-4 py-2 mt-12 text-gray-800 dark:text-gray-100 bg-gray-200 dark:bg-gray-800 rounded hover:bg-gray-300 dark:hover:bg-gray-700 transition-colors"
                                            onClick={() => {
                                                reset();
                                                navigate("/");
                                            }}
                                        >
                                            {t('btn.uploadAnother')}
                                        </button>
                                    </>
                                )}
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </Transition>
    );
};

export default Results;
