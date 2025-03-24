import { useShallow } from "zustand/react/shallow";
import useStore from "@/lib/store";
import { motion, AnimatePresence } from "framer-motion";
import Transition from "@/components/Transition";
import { useMemo, useState, useEffect } from "react";
import SuccessIcon from "@/lib/assets/success.svg";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import { useTranslation } from "react-i18next";

/**
 * Image component with fallback and error handling
 */
const DamageImage = ({ src, alt }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [error, setError] = useState(false);
  const [retryWithAlternate, setRetryWithAlternate] = useState(false);

  // Extract angle from alt text (e.g., "Front damage" -> "front")
  const angle = alt?.toLowerCase().replace(" damage", "").replace(" ", "_");

  const isBase64 =
    src && typeof src === "string" && src.startsWith("data:image/");

  // Try with alternate URL if the primary URL fails
  const imageUrl = useMemo(() => {
    console.log(
      `Image URL: ${src && src.substring(0, 30)}..., Angle: ${angle}, isBase64: ${isBase64}`
    );
    if (isBase64) {
      return src;
    }

    if (retryWithAlternate) {
      // Try uploaded photo if available
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

      // Try sample image as last resort
      const policyId = window.store?.getState()?.scope?.policyId;
      return policyId ? `/sample/${policyId}/${storeKey}.jpg` : null;
    }
    return src;
  }, [src, angle, retryWithAlternate, isBase64]);

  // Handle error by trying alternate source
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
      <div className="bg-gray-800 p-6 rounded border  text-gray-400 my-4 text-center">
        Image could not be loaded
        <p className="text-sm text-gray-400 mt-2">{alt}</p>
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
        className={`max-w-full rounded-md border max-h-64 mx-auto ${
          imageLoaded ? "opacity-100" : "opacity-0"
        }`}
        style={{ transition: "opacity 0.3s" }}
      />
      <p className="text-sm text-gray-400 mt-2">{alt}</p>
    </div>
  );
};

/**
 * Markdown custom components
 */
const markdownComponents = {
  h1: ({ node, ...props }) => (
    <h1 className="text-2xl font-bold mb-2 border-b pb-2" {...props} />
  ),
  h2: ({ node, ...props }) => (
    <h2 className="text-xl font-semibold mt-6 mb-3 border-b pb-1" {...props} />
  ),
  p: ({ node, ...props }) => <p className="my-2" {...props} />,
  strong: ({ node, ...props }) => <span className="font-bold" {...props} />,
  em: ({ node, ...props }) => (
    <span className="italic text-muted-foreground" {...props} />
  ),
  hr: () => <hr className="my-4 border-t" />,
  li: ({ node, ...props }) => <li className="ml-4 my-1" {...props} />,
  ul: ({ node, ...props }) => <ul className="my-2" {...props} />,
  ol: ({ node, ...props }) => <ol className="my-2 list-decimal ml-4" {...props} />,
  img: ({ node, ...props }) => <DamageImage {...props} />,
};

/**
 * Framer-motion animation config
 */
const animate = {
  initial: { opacity: 0.01 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: { type: "spring", stiffness: 100, damping: 20 },
};

/**
 * The main Results component
 */
const Results = () => {
  const [results, analyze, isThinking, scope, photos, reset] = useStore(
    useShallow((state) => [
      state.results,
      state.analyze,
      state.isThinking,
      state.scope,
      state.photos,
      state.reset,
    ])
  );

  // Make store available to image components for fallback
  useEffect(() => {
    window.store = { getState: () => ({ scope, photos }) };
    return () => {
      delete window.store;
    };
  }, [scope, photos]);

  const isSuccess = useMemo(() => !!results, [results]);
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();

  // Parse the results object to get both reports
  const { english_report, thai_report } = useMemo(() => {
    if (!results) return { english_report: "", thai_report: "" };

    try {
      // If results is already an object, use it directly
      if (typeof results === "object") {
        return results;
      }
      // If results is a string, try to parse it as JSON
      return JSON.parse(results);
    } catch (e) {
      console.error("Failed to parse results:", e);
      return { english_report: "", thai_report: "" };
    }
  }, [results]);

  const currentReport = useMemo(() => {
    return i18n.language === "th" ? thai_report : english_report;
  }, [english_report, thai_report, i18n.language]);

  useEffect(() => {
    analyze();
  }, [analyze]);

  return (
    <Transition>
      <AnimatePresence mode="sync">
        {isThinking ? (
          <motion.div key="thinking" {...animate} className="absolute w-full">
            <div className="flex justify-center">
              <div>
                <h1 className="text-3xl text-center">{t("results.loading")}</h1>
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
                  <>{t("results.error.message")}</>
                ) : (
                  <>
                    <SuccessIcon className="text-[limegreen] w-full max-w-[120px] mb-6 mt-4" />
                    <div className="sm:px-6 py-12 rounded-md sm:shadow-2xl dark:shadow-none max-w-3xl w-full my-6 sm:border">
                      {/**
                       * react-markdown v10+ uses urlTransform to override default URL checks.
                       * We check if (key === "src") is a base64 data URI and allow it.
                       * Return `undefined` otherwise so it falls back to default sanitization.
                       */}
                      <ReactMarkdown
                        components={markdownComponents}
                        urlTransform={(url, key) => {
                          // We only care about images (where key === 'src'):
                          if (key === "src" && url.startsWith("data:image/")) {
                            return url; // allow base64 data URIs
                          }
                          // For everything else, use default transform
                          return undefined; 
                        }}
                      >
                        {currentReport}
                      </ReactMarkdown>
                    </div>
                    <button
                      className="btn btn-secondary px-4 py-2 mt-12"
                      onClick={() => {
                        reset();
                        navigate("/");
                      }}
                    >
                      {t("btn.uploadAnother")}
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
