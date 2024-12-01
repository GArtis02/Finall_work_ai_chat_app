import React, { useState, useEffect } from 'react';
import { View, TextInput, Button, FlatList, Text, StyleSheet } from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const ChatScreen = () => {
  const [message, setMessage] = useState('');
  const [threadId, setThreadId] = useState('123456'); // Replace with the actual thread ID
  const [chatHistory, setChatHistory] = useState([]);
  const [apiUrl, setApiUrl] = useState(''); // API_URL state

  // Load the API_URL from AsyncStorage when the component mounts
  useEffect(() => {
    const loadApiUrl = async () => {
      try {
        const storedApiUrl = await AsyncStorage.getItem('API_URL');
        if (storedApiUrl) {
          setApiUrl(storedApiUrl);
        } else {
          console.warn('API_URL not found in AsyncStorage.');
        }
      } catch (error) {
        console.error('Error loading API_URL:', error);
      }
    };

    loadApiUrl();
  }, []);

  // Function to fetch conversation history
  const fetchConversationHistory = async () => {
    if (!apiUrl) {
      console.warn('API_URL is not set. Unable to fetch conversation history.');
      return;
    }

    try {
      console.log('Fetching conversation history...');
      const response = await axios.get(`${apiUrl}/conversation-history/`, {
        params: { thread_id: threadId },
      });
      if (response.data && response.data.conversation_history) {
        setChatHistory(response.data.conversation_history);
      } else {
        console.error('Unexpected response structure:', response.data);
      }
    } catch (error) {
      console.error('Error fetching conversation history:', error);
    }
  };

  // Fetch conversation history when the API_URL and thread ID are ready
  useEffect(() => {
    if (apiUrl) {
      fetchConversationHistory();
    }
  }, [apiUrl]);

  // Function to handle sending a message
  const sendMessage = async () => {
    if (message.trim() === '') {
      console.warn('Cannot send an empty message.');
      return;
    }

    if (!apiUrl) {
      console.warn('API_URL is not set. Unable to send message.');
      return;
    }

    try {
      console.log('Sending message...');
      const response = await axios.get(`${apiUrl}/send-message/`, {
        params: { thread_id: threadId, message },
      });

      if (response.data && response.data.response) {
        setChatHistory((prevHistory) => [
          ...prevHistory,
          { sender: 'user', content: message },
          { sender: 'assistant', content: response.data.response },
        ]);
        setMessage('');
      } else {
        console.error('Unexpected response format:', response.data);
      }
    } catch (error) {
      console.error('Error sending message:', error.response?.data || error.message);
    }
  };

  const renderMessageItem = ({ item }) => (
    <View
      style={[
        styles.messageContainer,
        item.sender === 'user' ? styles.userMessage : styles.assistantMessage,
      ]}
    >
      <Text>{item.content}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={chatHistory}
        renderItem={renderMessageItem}
        keyExtractor={(item, index) => index.toString()}
        style={styles.chatHistory}
      />
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={message}
          onChangeText={setMessage}
          placeholder="Type your message..."
        />
        <Button title="Send" onPress={sendMessage} />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 10 },
  chatHistory: { flex: 1, marginBottom: 10 },
  inputContainer: { flexDirection: 'row', alignItems: 'center' },
  input: {
    flex: 1,
    borderColor: '#ccc',
    borderWidth: 1,
    padding: 10,
    borderRadius: 5,
    marginRight: 10,
  },
  messageContainer: { padding: 10, borderRadius: 5, marginVertical: 5 },
  userMessage: { backgroundColor: '#dcf8c6', alignSelf: 'flex-end' },
  assistantMessage: { backgroundColor: '#f1f1f1', alignSelf: 'flex-start' },
});

export default ChatScreen;
