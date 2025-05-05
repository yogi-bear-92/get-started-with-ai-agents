import React, { useMemo } from "react";
import { Dropdown, Option, Label } from "@fluentui/react-components";
import { Theme, useThemeContext } from "./ThemeContext";

interface IDropdownItem {
  key: Theme;
  value: Theme;
  text: string;
}

export const ThemePicker: React.FC = () => {
  const { savedTheme, setTheme } = useThemeContext();

  const options: IDropdownItem[] = useMemo(
    () => [
      {
        key: "Light",
        value: "Light",
        text: "Light theme",
      },
      {
        key: "Dark",
        value: "Dark",
        text: "Dark theme",
      },
      {
        key: "System",
        value: "System",
        text: "System theme",
      },
    ],
    []
  );

  const selectedThemeText = useMemo(
    () =>
      options.find((opt) => opt.key === (savedTheme ?? "Light"))?.text ??
      "Light theme",
    [savedTheme, options]
  );

  const selectedOptions = useMemo(
    () => (savedTheme ? [savedTheme] : []),
    [savedTheme]
  );
  return (
    <>
      <Label htmlFor="ThemePickerDropdown">Theme</Label>
      <Dropdown
        id="ThemePickerDropdown"
        onOptionSelect={(_, { optionValue }) => {
          if (optionValue !== undefined) {
            setTheme(optionValue as Theme);
          }
        }}
        selectedOptions={selectedOptions}
        value={selectedThemeText}
      >
        {options.map((option) => (
          <Option key={option.key} value={option.value}>
            {option.text}
          </Option>
        ))}
      </Dropdown>
    </>
  );
};
