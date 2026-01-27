import React, { useState } from 'react';

/**
 * FormInput Component
 * Reusable input field with Tailwind styling
 */
const FormInput = ({
  label,
  type = 'text',
  name,
  placeholder,
  value,
  onChange,
  required = false,
  icon: Icon = null,
}) => {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <div className="mb-5">
      <label
        htmlFor={name}
        className="block text-sm font-medium text-gray-700 mb-2"
      >
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      <div className="relative">
        {Icon && (
          <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400">
            <Icon size={18} />
          </div>
        )}
        <input
          id={name}
          type={type}
          name={name}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          className={`w-full px-4 py-3 ${Icon ? 'pl-11' : ''} rounded-lg border-2 transition-all duration-200 outline-none
            ${
              isFocused
                ? 'border-primary-500 ring-2 ring-primary-100 shadow-md'
                : 'border-gray-200 hover:border-gray-300'
            }
            text-gray-900 placeholder-gray-400 font-medium`}
        />
      </div>
    </div>
  );
};

export default FormInput;
