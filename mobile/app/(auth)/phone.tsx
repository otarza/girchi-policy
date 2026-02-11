import React, { useState } from 'react';
import { View, Text, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { PhoneInput } from '@/src/components/ui/PhoneInput';
import { Button } from '@/src/components/ui/Button';
import { colors, typography, spacing } from '@/src/theme';

export default function PhoneScreen() {
  const router = useRouter();
  const [phone, setPhone] = useState('');

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.content}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <View>
          <Text style={styles.header}>ტელეფონის ნომერი</Text>
          <Text style={styles.subtitle}>შეიყვანეთ თქვენი ტელეფონის ნომერი</Text>
          <View style={styles.inputWrap}>
            <PhoneInput value={phone} onChangeText={setPhone} />
          </View>
        </View>

        <View style={styles.bottom}>
          <Button
            title="გაგრძელება"
            onPress={() => router.push('/(auth)/otp')}
            disabled={phone.length < 9}
          />
          <Text style={styles.privacy}>კონფიდენციალურობის პოლიტიკა</Text>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.surface,
  },
  content: {
    flex: 1,
    justifyContent: 'space-between',
    padding: spacing.xl,
  },
  header: {
    ...typography.h1,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  subtitle: {
    ...typography.body,
    color: colors.textSecondary,
    marginBottom: spacing.xl,
  },
  inputWrap: {
    marginTop: spacing.md,
  },
  bottom: {
    gap: spacing.md,
    paddingBottom: spacing.lg,
  },
  privacy: {
    ...typography.caption,
    color: colors.info,
    textAlign: 'center',
  },
});
