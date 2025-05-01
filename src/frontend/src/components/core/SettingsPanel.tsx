import type { JSX } from "react";
import {
  Button,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerHeaderTitle,
} from "@fluentui/react-components";
import { Dismiss24Regular } from "@fluentui/react-icons";

import styles from "./SettingsPanel.module.css";

export interface ISettingsPanelProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
}

export function SettingsPanel({
  isOpen = false,
  onOpenChange,
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
      </DrawerHeader>
      <DrawerBody className={styles.content}>
        {/* Content will go here */}
        <p>Settings panel content</p>
      </DrawerBody>
    </Drawer>
  );
}
