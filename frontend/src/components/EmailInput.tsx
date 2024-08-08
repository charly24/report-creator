import React from "react";

interface EmailInputProps {
  value: string;
  onChange: (value: string) => void;
}

const EmailInput: React.FC<EmailInputProps> = ({ value, onChange }) => {
  return (
    <div className="mb-4">
      <label
        htmlFor="email"
        className="block text-gray-700 text-sm font-bold mb-2"
      >
        Email:
      </label>
      <input
        type="email"
        id="email"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required
        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
      />
    </div>
  );
};

export default EmailInput;
