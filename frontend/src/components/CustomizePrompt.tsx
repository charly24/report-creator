import React, { useState, useMemo, useEffect } from "react";
import { getPrompt } from "../services/api";

interface CustomizePromptProps {
  onPromptUpdate: (splittingPrompt: string, formattingPrompt: string) => void;
  onChange: (value: boolean) => void;
}

const CustomizePrompt: React.FC<CustomizePromptProps> = ({
  onPromptUpdate,
  onChange,
}) => {
  const [isChecked, setIsChecked] = useState(false);

  const prompt = useMemo(() => {
    if (isChecked) {
      return getPrompt()
        .catch((error) => {
          console.error("Error fetching prompt:", error);
          return { splitting: "", formatting: "" };
        })
        .then((res) => res);
    }
    return Promise.resolve({ splitting: "", formatting: "" });
  }, [isChecked]);

  useEffect(() => {
    if (isChecked) {
      prompt.then(({ splitting, formatting }) => {
        onPromptUpdate(splitting, formatting);
      });
    }
  }, [isChecked, onPromptUpdate, prompt]);

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setIsChecked(e.target.checked);
    onChange(e.target.checked);
  };

  return (
    <div className="mb-4">
      <label className="block text-gray-700 text-sm font-bold mb-2">
        <input
          type="checkbox"
          checked={isChecked}
          onChange={handleCheckboxChange}
          className="ml-2"
        />
        &nbsp; Customize Prompt
      </label>
    </div>
  );
};

export default CustomizePrompt;
