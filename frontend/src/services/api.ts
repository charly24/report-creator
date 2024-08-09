const API_URL = "http://localhost:8000/process_text";

export const processText = async (
  inputText: string,
  splittingPrompt: string,
  formattingPrompt: string,
  email: string,
  apiKey: string
): Promise<void> => {
  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": "hoge",
    },
    body: JSON.stringify({
      input_text: inputText,
      splittingPrompt,
      formattingPrompt,
      email,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(
      errorData.message ||
        errorData.detail ||
        "An error occurred while processing the text."
    );
  }
};
