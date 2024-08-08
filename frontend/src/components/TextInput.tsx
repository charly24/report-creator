import React from "react";

interface TextInputProps {
  value: string;
  onChange: (value: string) => void;
}

const TextInput: React.FC<TextInputProps> = ({ value, onChange }) => {
  return (
    <div className="mb-4">
      <label
        htmlFor="input-text"
        className="block text-gray-700 text-sm font-bold mb-2"
      >
        Input Text:
      </label>
      <textarea
        id="input-text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={10}
        required
        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
      />
    </div>
  );
};

export default TextInput;
