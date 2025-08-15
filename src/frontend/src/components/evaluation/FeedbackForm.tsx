import React, { useState } from 'react';
import { Stack, Text, Button, Textarea, Label, SpinButton, Dialog, DialogTrigger, DialogSurface, DialogTitle, DialogBody, DialogActions } from '@fluentui/react-components';
import { ThumbLike16Regular, ThumbDislike16Regular, StarFilled } from '@fluentui/react-icons';

interface FeedbackFormProps {
    query: string;
    response: string;
    onFeedbackSubmitted?: () => void;
}

/**
 * User Feedback Collection Form Component
 * Collects user ratings and comments about agent responses
 */
const FeedbackForm: React.FC<FeedbackFormProps> = ({ query, response, onFeedbackSubmitted }) => {
    const [rating, setRating] = useState<number>(5);
    const [comments, setComments] = useState<string>('');
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [showDialog, setShowDialog] = useState<boolean>(false);

    // Submit feedback to the API
    const submitFeedback = async () => {
        try {
            setIsSubmitting(true);
            setError(null);

            const response = await fetch('/evaluation/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query,
                    response,
                    rating,
                    comments,
                }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.message || 'Failed to submit feedback');
            }

            // Reset form after successful submission
            setComments('');
            setRating(5);
            setShowDialog(false);

            // Notify parent component
            if (onFeedbackSubmitted) {
                onFeedbackSubmitted();
            }

        } catch (err) {
            setError(`Error submitting feedback: ${err instanceof Error ? err.message : String(err)}`);
            console.error('Error submitting feedback:', err);
        } finally {
            setIsSubmitting(false);
        }
    };

    // Generate star rating display
    const renderStars = (count: number) => {
        return Array(5)
            .fill(0)
            .map((_, index) => (
                <StarFilled
                    key={index}
                    style={{
                        color: index < count ? 'gold' : 'var(--colorNeutralBackground3)',
                        cursor: 'pointer',
                    }}
                    onClick={() => setRating(index + 1)}
                />
            ));
    };

    return (
        <>
            <Button
                icon={<ThumbLike16Regular />}
                appearance="subtle"
                onClick={() => setShowDialog(true)}
            >
                Rate this response
            </Button>

            <Dialog open={showDialog} onOpenChange={(e, data) => setShowDialog(data.open)}>
                <DialogSurface>
                    <DialogTitle>Rate Agent Response</DialogTitle>
                    <DialogBody>
                        <Stack tokens={{ childrenGap: 15 }}>
                            {error && (
                                <Text style={{ color: 'var(--colorStatusDangerForeground1)' }}>
                                    {error}
                                </Text>
                            )}

                            <Stack tokens={{ childrenGap: 5 }}>
                                <Label>Your rating</Label>
                                <Stack horizontal tokens={{ childrenGap: 5 }}>
                                    {renderStars(rating)}
                                </Stack>
                            </Stack>

                            <Stack tokens={{ childrenGap: 5 }}>
                                <Label>Comments (optional)</Label>
                                <Textarea
                                    value={comments}
                                    onChange={(e, data) => setComments(data.value)}
                                    placeholder="What did you think about this response?"
                                    style={{ minHeight: '100px' }}
                                />
                            </Stack>
                        </Stack>
                    </DialogBody>
                    <DialogActions>
                        <Button appearance="secondary" onClick={() => setShowDialog(false)}>Cancel</Button>
                        <Button
                            appearance="primary"
                            onClick={submitFeedback}
                            disabled={isSubmitting}
                        >
                            Submit Feedback
                        </Button>
                    </DialogActions>
                </DialogSurface>
            </Dialog>
        </>
    );
};

export default FeedbackForm;
