import { Redirect } from 'expo-router';
import { useApp } from '@/src/context/AppContext';

export default function Index() {
  const { isAuthenticated, isOnboarded } = useApp();

  if (!isAuthenticated) {
    return <Redirect href="/(auth)/welcome" />;
  }

  if (!isOnboarded) {
    return <Redirect href="/(onboarding)/ged-check" />;
  }

  return <Redirect href="/(tabs)" />;
}
