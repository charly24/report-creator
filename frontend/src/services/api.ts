const API_URL = 'https://your-cloud-function-url.com';

export const processText = async (
  inputText: string,
  splittingPrompt: string,
  formattingPrompt: string,
  email: string,
  apiKey: string
): Promise<void> => {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': apiKey,
    },
    body: JSON.stringify({
      inputText,
      splittingPrompt,
      formattingPrompt,
      email,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.message || 'An error occurred while processing the text.');
  }
};
