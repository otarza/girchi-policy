import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Avatar } from '@/src/components/ui/Avatar';
import { RoleBadge, StatusBadge, TierBadge } from '@/src/components/ui/Badge';
import { Card } from '@/src/components/ui/Card';
import { useApp } from '@/src/context/AppContext';
import { gamificationData } from '@/src/mock';
import { colors, typography, spacing } from '@/src/theme';

interface MenuItemProps {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  badge?: string;
  onPress?: () => void;
  danger?: boolean;
}

function MenuItem({ icon, label, badge, onPress, danger }: MenuItemProps) {
  return (
    <TouchableOpacity style={styles.menuItem} onPress={onPress} activeOpacity={0.7}>
      <Ionicons name={icon} size={22} color={danger ? colors.danger : colors.textSecondary} />
      <Text style={[styles.menuLabel, danger && styles.menuLabelDanger]}>{label}</Text>
      <View style={styles.menuRight}>
        {badge && (
          <View style={styles.menuBadge}>
            <Text style={styles.menuBadgeText}>{badge}</Text>
          </View>
        )}
        {!danger && <Ionicons name="chevron-forward" size={18} color={colors.divider} />}
      </View>
    </TouchableOpacity>
  );
}

export default function ProfileScreen() {
  const router = useRouter();
  const { user, logout } = useApp();

  const handleLogout = () => {
    logout();
    router.replace('/');
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <Text style={styles.title}>პროფილი</Text>

        {/* Profile Card */}
        <Card style={styles.profileCard}>
          <View style={styles.profileHeader}>
            <Avatar firstName={user.firstName} lastName={user.lastName} size={64} role={user.role} />
            <View style={styles.profileInfo}>
              <Text style={styles.profileName}>{user.firstName} {user.lastName}</Text>
              <View style={styles.badges}>
                <RoleBadge role={user.role} />
                <StatusBadge status={user.status} />
              </View>
            </View>
          </View>
          <View style={styles.profileDetails}>
            <Text style={styles.detailText}>{user.phoneMasked}</Text>
            <Text style={styles.detailText}>{user.precinctName}</Text>
            {user.role === 'geder' && (
              <Text style={styles.gedBalance}>GeD ბალანსი: {user.gedBalance}</Text>
            )}
          </View>
        </Card>

        {/* Menu */}
        <Card style={styles.menuCard}>
          <MenuItem
            icon="create-outline"
            label="პროფილის რედაქტირება"
          />
          <View style={styles.divider} />
          <MenuItem
            icon="bar-chart-outline"
            label="პროგრესი"
            onPress={() => router.push('/(tabs)/profile/progress')}
          />
          <View style={styles.divider} />
          <MenuItem
            icon="scale-outline"
            label="არბიტრაჟი"
            badge="0"
          />
          <View style={styles.divider} />
          <MenuItem
            icon="notifications-outline"
            label="შეტყობინებები"
            badge="3"
          />
          <View style={styles.divider} />
          <MenuItem
            icon="settings-outline"
            label="პარამეტრები"
          />
          <View style={styles.dividerThick} />
          <MenuItem
            icon="log-out-outline"
            label="გასვლა"
            danger
            onPress={handleLogout}
          />
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.md,
    gap: spacing.md,
    paddingBottom: spacing.xl,
  },
  title: {
    ...typography.h1,
    color: colors.textPrimary,
  },
  profileCard: {
    gap: spacing.md,
  },
  profileHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
  },
  profileInfo: {
    flex: 1,
    gap: spacing.xs,
  },
  profileName: {
    ...typography.h2,
    color: colors.textPrimary,
  },
  badges: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  profileDetails: {
    gap: spacing.xs,
  },
  detailText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  gedBalance: {
    ...typography.bodySmall,
    color: colors.primary,
    fontWeight: '600',
  },
  menuCard: {
    paddingHorizontal: 0,
    paddingVertical: spacing.xs,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.md,
    gap: spacing.sm,
  },
  menuLabel: {
    ...typography.body,
    color: colors.textPrimary,
    flex: 1,
  },
  menuLabelDanger: {
    color: colors.danger,
  },
  menuRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  menuBadge: {
    backgroundColor: colors.danger,
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 6,
  },
  menuBadgeText: {
    ...typography.caption,
    color: colors.white,
    fontWeight: '700',
    fontSize: 11,
  },
  divider: {
    height: 1,
    backgroundColor: colors.divider,
    marginHorizontal: spacing.md,
  },
  dividerThick: {
    height: 1,
    backgroundColor: colors.divider,
    marginHorizontal: spacing.md,
    marginVertical: spacing.xs,
  },
});
