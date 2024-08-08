import React from "react";

interface ApiKeyInputProps {
  value: string;
  onChange: (value: string) => void;
}

const ApiKeyInput: React.FC<ApiKeyInputProps> = ({ value, onChange }) => {
  return (
    <div className="mb-4">
      <label
        htmlFor="api-key"
        className="block text-gray-700 text-sm font-bold mb-2"
      >
        API Key:
      </label>
      <input
        type="password"
        id="api-key"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required
        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
      />
    </div>
  );
};

export default ApiKeyInput;
