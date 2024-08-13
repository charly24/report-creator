import React from "react";

interface PromptInputProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
}

const PromptInput: React.FC<PromptInputProps> = ({
  label,
  value,
  onChange,
}) => {
  return (
    <div className="mb-4 flex-1">
      <label
        htmlFor={`prompt-${label.toLowerCase()}`}
        className="block text-gray-700 text-sm font-bold mb-2"
      >
        {label}:
      </label>
      <textarea
        id={`prompt-${label.toLowerCase()}`}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={4}
        required={false}
        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
      />
    </div>
  );
};

export default PromptInput;
