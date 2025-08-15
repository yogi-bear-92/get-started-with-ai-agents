import type { JSX } from "react";
import {
  Button,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerHeaderTitle,
  Divider,
  makeStyles,
  tokens,
} from "@fluentui/react-components";
import { Dismiss24Regular } from "@fluentui/react-icons";

import styles from "./SettingsPanel.module.css";
import { ThemePicker } from "./theme/ThemePicker";
import { PersonalityPicker } from "./theme/PersonalityPicker";

const useStyles = makeStyles({
  section: {
    marginBottom: tokens.spacingVerticalL,
  },
  divider: {
    margin: `${tokens.spacingVerticalL} 0`,
  },
});

export interface ISettingsPanelProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  onPersonalityChange?: (personality: string) => void;
}

export function SettingsPanel({
  isOpen = false,
  onOpenChange,
  onPersonalityChange,
}: ISettingsPanelProps): JSX.Element {
  const localStyles = useStyles();

  const handlePersonalityChange = (personality: string) => {
    if (onPersonalityChange) {
      onPersonalityChange(personality);
    }
  };

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
        <div className={localStyles.section}>
          <PersonalityPicker onPersonalityChange={handlePersonalityChange} />
        </div>
        <Divider className={localStyles.divider} />
        <div className={localStyles.section}>
          <ThemePicker />
        </div>
      </DrawerBody>
    </Drawer>
  );
}
