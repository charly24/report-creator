import React, { useState } from "react";
import TextInput from "./components/TextInput";
import PromptInput from "./components/PromptInput";
import EmailInput from "./components/EmailInput";
import ApiKeyInput from "./components/ApiKeyInput";
import { processText } from "./services/api";

const App: React.FC = () => {
  const [inputText, setInputText] = useState("");
  const [splittingPrompt, setSplittingPrompt] = useState("");
  const [formattingPrompt, setFormattingPrompt] = useState("");
  const [email, setEmail] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsProcessing(true);
    setError(null);

    try {
      await processText(
        inputText,
        splittingPrompt,
        formattingPrompt,
        email,
        apiKey
      );
      alert(
        "Text processed successfully! Check your email for the formatted result."
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "An error occurred. Please try again later."
      );
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Text Formatting Tool</h1>
      <form onSubmit={handleSubmit} className="space-y-6">
        <TextInput value={inputText} onChange={setInputText} />

        <div className="flex space-x-4">
          <PromptInput
            label="Splitting Prompt"
            value={splittingPrompt}
            onChange={setSplittingPrompt}
          />
          <PromptInput
            label="Formatting Prompt"
            value={formattingPrompt}
            onChange={setFormattingPrompt}
          />
        </div>

        <div className="flex space-x-4">
          <div className="flex-1">
            <EmailInput value={email} onChange={setEmail} />
          </div>
          <div className="flex-1">
            <ApiKeyInput value={apiKey} onChange={setApiKey} />
          </div>
        </div>

        <button
          type="submit"
          disabled={isProcessing}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
        >
          {isProcessing ? "Processing..." : "Process Text"}
        </button>
      </form>
      {error && <div className="text-red-500 mt-4">{error}</div>}
    </div>
  );
};

export default App;
