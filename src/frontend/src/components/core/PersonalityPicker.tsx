import type { JSX } from "react";
import {
  Radio,
  RadioGroup,
  Text,
  makeStyles,
  tokens,
} from "@fluentui/react-components";
import { useState, useEffect } from "react";

const useStyles = makeStyles({
  container: {
    display: "flex",
    flexDirection: "column",
    gap: tokens.spacingVerticalM,
  },
  radioGroup: {
    display: "flex",
    flexDirection: "column",
    gap: tokens.spacingVerticalS,
  },
  radioItem: {
    display: "flex",
    flexDirection: "column",
    gap: tokens.spacingVerticalXS,
  },
  description: {
    marginLeft: "24px",
    color: tokens.colorNeutralForeground3,
    fontSize: tokens.fontSizeBase200,
  },
  title: {
    fontSize: tokens.fontSizeBase300,
    fontWeight: tokens.fontWeightSemibold,
    marginBottom: tokens.spacingVerticalS,
  },
});

export interface PersonalityOption {
  id: string;
  name: string;
  description: string;
}

const personalities: PersonalityOption[] = [
  {
    id: "default",
    name: "General Assistant",
    description: "General purpose assistant for all types of queries"
  },
  {
    id: "customer_service",
    name: "Customer Service",
    description: "Friendly customer service focused on helping customers"
  },
  {
    id: "technical_support",
    name: "Technical Support",
    description: "Technical expert providing detailed troubleshooting support"
  },
  {
    id: "sales_assistant",
    name: "Sales Assistant",
    description: "Enthusiastic sales expert helping customers find the right products"
  },
  {
    id: "concierge",
    name: "Concierge",
    description: "Refined concierge providing personalized assistance and recommendations"
  }
];

export interface IPersonalityPickerProps {
  selectedPersonality?: string;
  onPersonalityChange?: (personalityId: string) => void;
}

export function PersonalityPicker({
  selectedPersonality = "default",
  onPersonalityChange,
}: IPersonalityPickerProps): JSX.Element {
  const styles = useStyles();
  const [currentPersonality, setCurrentPersonality] = useState(selectedPersonality);

  useEffect(() => {
    setCurrentPersonality(selectedPersonality);
  }, [selectedPersonality]);

  const handlePersonalityChange = (personalityId: string) => {
    setCurrentPersonality(personalityId);
    onPersonalityChange?.(personalityId);
  };

  return (
    <div className={styles.container}>
      <Text className={styles.title}>Agent Personality</Text>
      <RadioGroup
        className={styles.radioGroup}
        value={currentPersonality}
        onChange={(_, data) => handlePersonalityChange(data.value)}
      >
        {personalities.map((personality) => (
          <div key={personality.id} className={styles.radioItem}>
            <Radio
              value={personality.id}
              label={personality.name}
            />
            <Text className={styles.description}>
              {personality.description}
            </Text>
          </div>
        ))}
      </RadioGroup>
    </div>
  );
}