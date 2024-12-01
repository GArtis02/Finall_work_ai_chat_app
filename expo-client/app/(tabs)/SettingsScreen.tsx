
import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const SettingsScreen = () => {
  const [apiUrl, setApiUrl] = useState('');

  useEffect(() => {
    const loadConfig = async () => {
      try {
        const savedUrl = await AsyncStorage.getItem('API_URL');
        if (savedUrl) setApiUrl(savedUrl);
      } catch (err) {
        console.error('Failed to load config:', err);
      }
    };
    loadConfig();
  }, []);

  const saveConfig = async () => {
    try {
      await AsyncStorage.setItem('API_URL', apiUrl);
      Alert.alert('Success', 'API_URL updated!');
    } catch (err) {
      console.error('Failed to save config:', err);
      Alert.alert('Error', 'Failed to save the settings.');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.label}>API_URL:</Text>
      <TextInput
        style={styles.input}
        value={apiUrl}
        onChangeText={setApiUrl}
        placeholder="Enter API URL"
      />
      <Button title="Save" onPress={saveConfig} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    justifyContent: 'center',
  },
  label: {
    fontSize: 16,
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 4,
    padding: 8,
    marginBottom: 16,
  },
});

export default SettingsScreen;
