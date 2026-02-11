import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Avatar } from '@/src/components/ui/Avatar';
import { RoleBadge } from '@/src/components/ui/Badge';
import { colors, typography, spacing } from '@/src/theme';
import type { Member } from '@/src/mock';

interface MemberCardProps {
  member: Member;
}

export function MemberCard({ member }: MemberCardProps) {
  return (
    <View style={styles.container}>
      <Avatar firstName={member.firstName} lastName={member.lastName} role={member.role} size={40} />
      <View style={styles.info}>
        <Text style={styles.name}>{member.firstName} {member.lastName}</Text>
        <Text style={styles.date}>{member.joinDate}</Text>
      </View>
      <RoleBadge role={member.role} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    gap: spacing.sm,
  },
  info: {
    flex: 1,
  },
  name: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: '500',
  },
  date: {
    ...typography.caption,
    color: colors.textSecondary,
  },
});
