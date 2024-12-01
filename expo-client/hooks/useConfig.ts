
import AsyncStorage from '@react-native-async-storage/async-storage';

export const getConfig = async () => {
  try {
    const apiUrl = await AsyncStorage.getItem('API_URL');
    return {
      API_URL: apiUrl || '', // Fallback to empty if not set
    };
  } catch (err) {
    console.error('Failed to load config:', err);
    return { API_URL: '' };
  }
};
