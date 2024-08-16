import React, { useState } from "react";
import TextInput from "./components/TextInput";
import PromptInput from "./components/PromptInput";
import EmailInput from "./components/EmailInput";
import ApiKeyInput from "./components/ApiKeyInput";
import CustomizePrompt from "./components/CustomizePrompt";
import { processText, getPrompt } from "./services/api";

const App: React.FC = () => {
  const [inputText, setInputText] = useState("");
  const [isCustomizePtompt, setIsCustomizePtompt] = useState(false);
  const [splittingPrompt, setSplittingPrompt] = useState("");
  const [formattingPrompt, setFormattingPrompt] = useState("");
  const [email, setEmail] = useState(
    process.env.NODE_ENV === "development" ? "ryo.nagaoka@gmail.com" : ""
  );
  const [apiKey, setApiKey] = useState("mindset2024");
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
          <div className="flex-1">
            <EmailInput value={email} onChange={setEmail} />
          </div>
          <div className="flex-1">
            <ApiKeyInput value={apiKey} onChange={setApiKey} />
          </div>
        </div>

        {/* <CustomizePrompt
          onPromptUpdate={(splitting, formatting) => {
            setSplittingPrompt(splitting);
            setFormattingPrompt(formatting);
          }}
          onChange={setIsCustomizePtompt}
        /> */}
        {isCustomizePtompt && (
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
        )}

        <button
          type="submit"
          disabled={isProcessing}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
        >
          {isProcessing ? "Processing..." : "Process Text"}
        </button>
      </form>
      {error && <div className="text-red-500 mt-4">{error}</div>}
      <h2 className="text-3xl font-bold mt-6">利用上の注意</h2>
      <ul className="list-disc pl-5 space-y-2">
        <li>
          tl:dvやLINE CLOVA
          Noteなど文字起こしされたタイムスタンプ付きの文章をそのまま貼り付けて、Process
          Textを押すことでフォーマットし、結果は入力したメールアドレスに送付されます。
        </li>
        <li>
          フォーマットには文字数によりますが数分程度かかります。その間、このページを閉じたり、リロードしたりしないでください。
        </li>
        <li>
          処理の最中にエラーが発生した場合は、エラーメッセージが表示されます。再実行することで正常に動作することもありますが、繰り返す場合は
          <a
            className="font-medium text-blue-600 dark:text-blue-500 hover:underline"
            href="https://www.facebook.com/ryo.nagaoka"
            target="_blank"
            rel="noreferrer"
          >
            長岡
          </a>
          までご連絡いただくかどこかでmentionしてください。
        </li>
        <li>
          GCP利用時のクーポン$300を利用しているため無償で提供できるようにしていますが、1回の利用あたり数円程度発生するため、節度を守った利用をお願いします。
        </li>
        <li>
          入力された文章はフォーマットした後に原則として破棄していますが、一部の利用情報は集計のため収集しています。また、Google
          GeminiというAIを利用しておりますが、学習には利用しない設定です。
        </li>
        <li>
          文字起こしが間違っている場合もありますし、このツールは100%の精度を保証するものではありません。そのため、
          <strong>
            レポート提出の前に読む方のことを考えて必ず確認・修正した後に提出してください
          </strong>
          。
        </li>
      </ul>
      <h2 className="text-3xl font-bold mt-6">フォーマットの方針</h2>
      <ul className="list-disc pl-5 space-y-2">
        <li>
          文章整形:
          文意を変えずに誤りを修正し、不要なスペースやフィラーワードを削除します。不明瞭な部分は[不明瞭]と記載し、可能な限り文脈から補完します。
        </li>
        <li>
          発言者の表記: コーチとクライアントをそれぞれ「コ: 」「ク:
          」と表記します。
        </li>
        <li>
          発言の整形:
          同じ人の連続した発言は1行にまとめ、トピックが変わる場合は2行改行。相槌や不要な表現は削除します。
        </li>
        <li>
          頻出キーワードの修正: 誤りやすいキーワードを注意して修正します。
        </li>
      </ul>
    </div>
  );
};

export default App;
