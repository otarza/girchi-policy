import React from 'react';
import { TouchableOpacity, Text, StyleSheet, type ViewStyle } from 'react-native';
import { colors, typography, borderRadius, spacing } from '@/src/theme';

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'text';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: ButtonVariant;
  disabled?: boolean;
  style?: ViewStyle;
}

export function Button({ title, onPress, variant = 'primary', disabled = false, style }: ButtonProps) {
  const variantStyles = variants[variant];

  return (
    <TouchableOpacity
      style={[
        styles.base,
        variantStyles.container,
        disabled && styles.disabled,
        style,
      ]}
      onPress={onPress}
      disabled={disabled}
      activeOpacity={0.7}
    >
      <Text style={[styles.text, variantStyles.text, disabled && styles.disabledText]}>
        {title}
      </Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  base: {
    height: 48,
    borderRadius: borderRadius.md,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.lg,
  },
  text: {
    ...typography.button,
  },
  disabled: {
    opacity: 0.5,
  },
  disabledText: {
    opacity: 0.7,
  },
});

const variants = {
  primary: StyleSheet.create({
    container: { backgroundColor: colors.primary },
    text: { color: colors.white },
  }),
  secondary: StyleSheet.create({
    container: { backgroundColor: colors.transparent, borderWidth: 1.5, borderColor: colors.primary },
    text: { color: colors.primary },
  }),
  danger: StyleSheet.create({
    container: { backgroundColor: colors.danger },
    text: { color: colors.white },
  }),
  text: StyleSheet.create({
    container: { backgroundColor: colors.transparent, height: 40 },
    text: { color: colors.primary },
  }),
};
