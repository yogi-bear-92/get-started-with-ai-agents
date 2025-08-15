import React, { useState, useEffect } from "react";
import {
    Dropdown,
    Option,
    Label,
    OptionGroup,
    Spinner,
    makeStyles,
    tokens,
} from "@fluentui/react-components";

const useStyles = makeStyles({
    container: {
        display: "flex",
        flexDirection: "column",
        gap: tokens.spacingVerticalM,
        marginBottom: tokens.spacingVerticalXL,
    },
    label: {
        marginBottom: tokens.spacingVerticalS,
    },
    dropdown: {
        maxWidth: "100%",
    },
    description: {
        fontSize: tokens.fontSizeBase200,
        color: tokens.colorNeutralForeground2,
        marginTop: tokens.spacingVerticalS,
    },
});

interface PersonalityOption {
    id: string;
    name: string;
    description: string;
}

export interface PersonalityPickerProps {
    onPersonalityChange?: (personality: string) => void;
}

export const PersonalityPicker: React.FC<PersonalityPickerProps> = ({
    onPersonalityChange,
}) => {
    const styles = useStyles();
    const [loading, setLoading] = useState(true);
    const [personalities, setPersonalities] = useState<PersonalityOption[]>([]);
    const [selectedPersonality, setSelectedPersonality] = useState<string>("default");
    const [currentPersonality, setCurrentPersonality] = useState<string | null>(null);

    // Predefined personality options
    const personalityOptions: PersonalityOption[] = [
        {
            id: "default",
            name: "Default",
            description: "Basic agent behavior with standard knowledge retrieval instructions.",
        },
        {
            id: "customer_service",
            name: "Customer Service",
            description: "Polite and helpful assistant focused on customer support scenarios.",
        },
        {
            id: "technical_support",
            name: "Technical Support",
            description: "Technical specialist providing clear and accurate technical information.",
        },
        {
            id: "sales_assistant",
            name: "Sales Assistant",
            description: "Sales-focused assistant that helps customers find the right products.",
        },
        {
            id: "concierge",
            name: "Concierge",
            description: "Sophisticated concierge providing personalized assistance and recommendations.",
        },
    ];

    // Fetch the current personality from the backend on component mount
    useEffect(() => {
        const fetchCurrentPersonality = async () => {
            try {
                // Try to get personality from local storage first
                const localPersonality = localStorage.getItem("agentPersonality");

                // Then try to get from backend
                let backendPersonality = "default";
                try {
                    const response = await fetch('/agent/personality');
                    if (response.ok) {
                        const data = await response.json();
                        backendPersonality = data.personality;
                    }
                } catch (apiError) {
                    console.warn("Failed to fetch personality from API, using local value:", apiError);
                }

                // Use local storage value if available, otherwise use backend value
                const finalPersonality = localPersonality || backendPersonality || "default";
                setCurrentPersonality(finalPersonality);
                setSelectedPersonality(finalPersonality);
            } catch (error) {
                console.error("Failed to fetch current personality:", error);
                setCurrentPersonality("default");
                setSelectedPersonality("default");
            } finally {
                setLoading(false);
            }
        };

        setPersonalities(personalityOptions);
        fetchCurrentPersonality();
    }, []);

    const handlePersonalityChange = (_: any, data: { optionValue?: string }) => {
        const newPersonality = data.optionValue || "default";
        setSelectedPersonality(newPersonality);

        // Save to local storage
        localStorage.setItem("agentPersonality", newPersonality);

        // Optionally update backend - in a real implementation this would be uncommented
        // fetch('/agent/personality', {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify({ personality: newPersonality })
        // });

        if (onPersonalityChange) {
            onPersonalityChange(newPersonality);
        }
    };

    // Find the description for the selected personality
    const selectedDescription = personalities.find(p => p.id === selectedPersonality)?.description || "";

    if (loading) {
        return <Spinner label="Loading personalities..." />;
    }

    return (
        <div className={styles.container}>
            <Label className={styles.label} weight="semibold">
                Agent Personality
            </Label>
            <Dropdown
                className={styles.dropdown}
                value={personalityOptions.find(p => p.id === selectedPersonality)?.name}
                selectedOptions={[selectedPersonality]}
                onOptionSelect={handlePersonalityChange}
            >
                <OptionGroup label="Select a personality">
                    {personalities.map((personality) => (
                        <Option key={personality.id} value={personality.id}>
                            {personality.name}
                        </Option>
                    ))}
                </OptionGroup>
            </Dropdown>
            {selectedDescription && (
                <div className={styles.description}>{selectedDescription}</div>
            )}
        </div>
    );
};
