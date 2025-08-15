import { ReactNode, useState, useEffect } from "react";
import {
  Dropdown,
  Option,
  Text,
  Spinner,
  makeStyles,
  tokens,
} from "@fluentui/react-components";
import { PersonRegular, InfoRegular } from "@fluentui/react-icons";

const useStyles = makeStyles({
  container: {
    display: "flex",
    flexDirection: "column",
    gap: tokens.spacingVerticalM,
    padding: tokens.spacingVerticalM,
    borderRadius: tokens.borderRadiusMedium,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground2,
  },
  header: {
    display: "flex",
    alignItems: "center",
    gap: tokens.spacingHorizontalS,
  },
  selectorRow: {
    display: "flex",
    alignItems: "center",
    gap: tokens.spacingHorizontalM,
  },
  dropdown: {
    minWidth: "200px",
  },
  description: {
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorNeutralForeground2,
    fontStyle: "italic",
    marginTop: tokens.spacingVerticalXS,
  },
  warning: {
    color: tokens.colorPaletteYellowForeground1,
    fontSize: tokens.fontSizeBase200,
    display: "flex",
    alignItems: "center",
    gap: tokens.spacingHorizontalXS,
  },
});

interface Personality {
  id: string;
  name: string;
  description: string;
  temperature: number;
  current: boolean;
}

interface PersonalitySelectorProps {
  onPersonalityChange?: (personalityId: string) => void;
}

export function PersonalitySelector({ onPersonalityChange }: PersonalitySelectorProps): ReactNode {
  const styles = useStyles();
  const [personalities, setPersonalities] = useState<Personality[]>([]);
  const [currentPersonality, setCurrentPersonality] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [selectedPersonality, setSelectedPersonality] = useState<string>("");

  useEffect(() => {
    loadPersonalities();
  }, []);

  const loadPersonalities = async () => {
    try {
      const response = await fetch("/personalities");
      if (response.ok) {
        const data = await response.json();
        setPersonalities(data.personalities);
        setCurrentPersonality(data.current);
        setSelectedPersonality(data.current);
      } else {
        console.error("Failed to load personalities");
      }
    } catch (error) {
      console.error("Error loading personalities:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePersonalityChange = (personalityId: string) => {
    setSelectedPersonality(personalityId);
    if (onPersonalityChange) {
      onPersonalityChange(personalityId);
    }
  };

  const getSelectedPersonality = () => {
    return personalities.find(p => p.id === selectedPersonality);
  };

  const hasChanged = selectedPersonality !== currentPersonality;

  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <PersonRegular />
          <Text weight="semibold">Agent Personality</Text>
        </div>
        <Spinner size="small" label="Loading personalities..." />
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <PersonRegular />
        <Text weight="semibold">Agent Personality</Text>
      </div>
      
      <div className={styles.selectorRow}>
        <Dropdown
          className={styles.dropdown}
          placeholder="Select personality"
          value={personalities.find(p => p.id === selectedPersonality)?.name || ""}
          onOptionSelect={(_, data) => handlePersonalityChange(data.optionValue as string)}
        >
          {personalities.map((personality) => (
            <Option key={personality.id} value={personality.id}>
              {personality.name}
            </Option>
          ))}
        </Dropdown>
      </div>

      {getSelectedPersonality() && (
        <Text className={styles.description}>
          {getSelectedPersonality()?.description}
        </Text>
      )}

      {hasChanged && (
        <div className={styles.warning}>
          <InfoRegular />
          <Text>
            Personality changes require agent recreation. Please restart the application or deploy with azd to apply changes.
          </Text>
        </div>
      )}
    </div>
  );
}