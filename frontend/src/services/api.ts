const API_URL =
  process.env.NODE_ENV === "development"
    ? "http://localhost:8000"
    : "https://on-request-ehm3c6ii6q-uc.a.run.app";

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
      "X-API-Key": apiKey,
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
      errorData.description || "An error occurred while processing the text."
    );
  }
};

export const getPrompt = async (): Promise<{
  splitting: string;
  formatting: string;
}> => {
  return { splitting: "splitting", formatting: "formatting" };
};
