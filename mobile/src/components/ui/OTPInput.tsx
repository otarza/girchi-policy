import React, { useRef, useState } from 'react';
import { View, TextInput, StyleSheet } from 'react-native';
import { colors, typography, borderRadius, spacing } from '@/src/theme';

interface OTPInputProps {
  length?: number;
  onComplete: (code: string) => void;
}

export function OTPInput({ length = 6, onComplete }: OTPInputProps) {
  const [values, setValues] = useState<string[]>(Array(length).fill(''));
  const refs = useRef<(TextInput | null)[]>([]);

  const handleChange = (text: string, index: number) => {
    // Handle paste
    if (text.length > 1) {
      const digits = text.replace(/\D/g, '').slice(0, length);
      const newValues = Array(length).fill('');
      digits.split('').forEach((d, i) => { newValues[i] = d; });
      setValues(newValues);
      if (digits.length === length) onComplete(digits);
      refs.current[Math.min(digits.length, length - 1)]?.focus();
      return;
    }

    const newValues = [...values];
    newValues[index] = text;
    setValues(newValues);

    if (text && index < length - 1) {
      refs.current[index + 1]?.focus();
    }

    const code = newValues.join('');
    if (code.length === length && !newValues.includes('')) {
      onComplete(code);
    }
  };

  const handleKeyPress = (e: any, index: number) => {
    if (e.nativeEvent.key === 'Backspace' && !values[index] && index > 0) {
      refs.current[index - 1]?.focus();
      const newValues = [...values];
      newValues[index - 1] = '';
      setValues(newValues);
    }
  };

  return (
    <View style={styles.container}>
      {values.map((val, i) => (
        <TextInput
          key={i}
          ref={r => { refs.current[i] = r; }}
          style={[styles.box, val ? styles.boxFilled : null]}
          value={val}
          onChangeText={t => handleChange(t, i)}
          onKeyPress={e => handleKeyPress(e, i)}
          keyboardType="number-pad"
          maxLength={i === 0 ? length : 1}
          selectTextOnFocus
        />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    gap: spacing.sm + 2,
    justifyContent: 'center',
  },
  box: {
    width: 48,
    height: 56,
    borderWidth: 1.5,
    borderColor: colors.divider,
    borderRadius: borderRadius.md,
    textAlign: 'center',
    fontSize: 24,
    fontWeight: '600',
    color: colors.textPrimary,
    backgroundColor: colors.surface,
  },
  boxFilled: {
    borderColor: colors.primary,
  },
});
