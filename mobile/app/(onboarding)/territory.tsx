import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, FlatList } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Button } from '@/src/components/ui/Button';
import { colors, typography, spacing, borderRadius } from '@/src/theme';
import { mockRegions, mockDistricts, mockPrecincts } from '@/src/mock';
import type { Region, District, Precinct } from '@/src/mock';

type Step = 'region' | 'district' | 'precinct';

export default function TerritoryScreen() {
  const router = useRouter();
  const [step, setStep] = useState<Step>('region');
  const [selectedRegion, setSelectedRegion] = useState<Region | null>(null);
  const [selectedDistrict, setSelectedDistrict] = useState<District | null>(null);
  const [selectedPrecinct, setSelectedPrecinct] = useState<Precinct | null>(null);

  const handleRegionSelect = (region: Region) => {
    setSelectedRegion(region);
    setSelectedDistrict(null);
    setSelectedPrecinct(null);
    setStep('district');
  };

  const handleDistrictSelect = (district: District) => {
    setSelectedDistrict(district);
    setSelectedPrecinct(null);
    setStep('precinct');
  };

  const handlePrecinctSelect = (precinct: Precinct) => {
    setSelectedPrecinct(precinct);
  };

  const handleBack = () => {
    if (step === 'precinct') setStep('district');
    else if (step === 'district') setStep('region');
  };

  const titles: Record<Step, string> = {
    region: 'აირჩიეთ რეგიონი',
    district: 'აირჩიეთ ოლქი',
    precinct: 'აირჩიეთ უბანი',
  };

  const breadcrumb = [
    selectedRegion?.name,
    selectedDistrict?.name,
  ].filter(Boolean).join(' > ');

  const filteredDistricts = mockDistricts.filter(d => d.regionId === selectedRegion?.id);
  const filteredPrecincts = mockPrecincts.filter(p => p.districtId === selectedDistrict?.id);

  const renderRegion = ({ item }: { item: Region }) => (
    <TouchableOpacity style={styles.row} onPress={() => handleRegionSelect(item)} activeOpacity={0.7}>
      <Text style={styles.rowText}>{item.name}</Text>
      <Ionicons name="chevron-forward" size={18} color={colors.textSecondary} />
    </TouchableOpacity>
  );

  const renderDistrict = ({ item }: { item: District }) => (
    <TouchableOpacity style={styles.row} onPress={() => handleDistrictSelect(item)} activeOpacity={0.7}>
      <Text style={styles.rowText}>{item.name}</Text>
      <Ionicons name="chevron-forward" size={18} color={colors.textSecondary} />
    </TouchableOpacity>
  );

  const renderPrecinct = ({ item }: { item: Precinct }) => (
    <TouchableOpacity
      style={[styles.row, selectedPrecinct?.id === item.id && styles.rowSelected]}
      onPress={() => handlePrecinctSelect(item)}
      activeOpacity={0.7}
    >
      <View style={styles.rowInfo}>
        <Text style={styles.rowText}>{item.name}</Text>
        <Text style={styles.rowMeta}>{item.memberCount} წევრი · {item.groupCount} ათეული</Text>
      </View>
      {selectedPrecinct?.id === item.id && (
        <Ionicons name="checkmark-circle" size={22} color={colors.primary} />
      )}
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        {step !== 'region' && (
          <TouchableOpacity onPress={handleBack} style={styles.backBtn}>
            <Ionicons name="arrow-back" size={22} color={colors.textPrimary} />
          </TouchableOpacity>
        )}
        <View>
          <Text style={styles.title}>{titles[step]}</Text>
          {breadcrumb ? <Text style={styles.breadcrumb}>{breadcrumb}</Text> : null}
        </View>
      </View>

      <View style={styles.list}>
        {step === 'region' && (
          <FlatList data={mockRegions} renderItem={renderRegion} keyExtractor={i => i.id} />
        )}
        {step === 'district' && (
          <FlatList data={filteredDistricts} renderItem={renderDistrict} keyExtractor={i => i.id} />
        )}
        {step === 'precinct' && (
          <FlatList data={filteredPrecincts} renderItem={renderPrecinct} keyExtractor={i => i.id} />
        )}
      </View>

      {selectedPrecinct && (
        <View style={styles.bottom}>
          <Button
            title="დადასტურება"
            onPress={() => router.push('/(onboarding)/complete')}
          />
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.surface,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.xl,
    paddingBottom: spacing.md,
    gap: spacing.sm,
  },
  backBtn: {
    padding: spacing.xs,
  },
  title: {
    ...typography.h2,
    color: colors.textPrimary,
  },
  breadcrumb: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
  list: {
    flex: 1,
    paddingHorizontal: spacing.xl,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.divider,
  },
  rowSelected: {
    backgroundColor: colors.primarySurface,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.sm,
    marginHorizontal: -spacing.sm,
  },
  rowInfo: {
    flex: 1,
  },
  rowText: {
    ...typography.body,
    color: colors.textPrimary,
  },
  rowMeta: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
  bottom: {
    padding: spacing.xl,
  },
});
