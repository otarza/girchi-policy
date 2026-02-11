import React from 'react';
import { View, Text, TextInput, StyleSheet } from 'react-native';
import { colors, typography, borderRadius, spacing } from '@/src/theme';

interface PhoneInputProps {
  value: string;
  onChangeText: (text: string) => void;
}

export function PhoneInput({ value, onChangeText }: PhoneInputProps) {
  const handleChange = (text: string) => {
    const digits = text.replace(/\D/g, '').slice(0, 9);
    onChangeText(digits);
  };

  return (
    <View style={styles.container}>
      <View style={styles.prefix}>
        <Text style={styles.flag}>🇬🇪</Text>
        <Text style={styles.code}>+995</Text>
      </View>
      <TextInput
        style={styles.input}
        value={value}
        onChangeText={handleChange}
        keyboardType="phone-pad"
        placeholder="5XX XX XX XX"
        placeholderTextColor={colors.divider}
        maxLength={9}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    borderWidth: 1.5,
    borderColor: colors.divider,
    borderRadius: borderRadius.md,
    backgroundColor: colors.surface,
    overflow: 'hidden',
  },
  prefix: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    backgroundColor: colors.background,
    borderRightWidth: 1,
    borderRightColor: colors.divider,
    gap: spacing.xs,
  },
  flag: {
    fontSize: 20,
  },
  code: {
    ...typography.body,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  input: {
    flex: 1,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    ...typography.body,
    color: colors.textPrimary,
    fontSize: 18,
    letterSpacing: 1,
  },
});
