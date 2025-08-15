import type { JSX } from "react";
import {
  Button,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerHeaderTitle,
  Divider,
} from "@fluentui/react-components";
import { Dismiss24Regular } from "@fluentui/react-icons";

import styles from "./SettingsPanel.module.css";
import { ThemePicker } from "./theme/ThemePicker";
import { PersonalityPicker } from "./PersonalityPicker";

export interface ISettingsPanelProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  selectedPersonality?: string;
  onPersonalityChange?: (personalityId: string) => void;
}

export function SettingsPanel({
  isOpen = false,
  onOpenChange,
  selectedPersonality,
  onPersonalityChange,
}: ISettingsPanelProps): JSX.Element {
  return (
    <Drawer
      className={styles.panel}
      onOpenChange={(_, { open }) => {
        onOpenChange(open);
      }}
      open={isOpen}
      position="end"
    >
      <DrawerHeader>
        <DrawerHeaderTitle
          action={
            <div>
              <Button
                appearance="subtle"
                icon={<Dismiss24Regular />}
                onClick={() => {
                  onOpenChange(false);
                }}
              />
            </div>
          }
        >
          Settings
        </DrawerHeaderTitle>
      </DrawerHeader>{" "}
      <DrawerBody className={styles.content}>
        <PersonalityPicker
          selectedPersonality={selectedPersonality}
          onPersonalityChange={onPersonalityChange}
        />
        <Divider />
        <ThemePicker />
      </DrawerBody>
    </Drawer>
  );
}
