import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Animated,
  Dimensions,
  StatusBar,
  Alert,
  SafeAreaView,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

const { width, height } = Dimensions.get('window');

export default function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState('');
  const [animatedValue] = useState(new Animated.Value(0));

  // Animation for recording button
  const startRecordingAnimation = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(animatedValue, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(animatedValue, {
          toValue: 0,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  };

  const stopRecordingAnimation = () => {
    animatedValue.stopAnimation();
    animatedValue.setValue(0);
  };

  const handleRecordPress = () => {
    if (!isRecording) {
      setIsRecording(true);
      startRecordingAnimation();
      Alert.alert(
        'Recording Started',
        'Speak your emotions... (This is a demo - voice recording will be implemented next)',
        [
          {
            text: 'Stop Recording',
            onPress: () => {
              setIsRecording(false);
              stopRecordingAnimation();
              simulateEmotionDetection();
            },
          },
        ]
      );
    }
  };

  // Simulate emotion detection for demo
  const simulateEmotionDetection = () => {
    const emotions = ['happy', 'sad', 'calm', 'excited', 'thoughtful'];
    const randomEmotion = emotions[Math.floor(Math.random() * emotions.length)];
    setCurrentEmotion(randomEmotion);
    
    setTimeout(() => {
      Alert.alert(
        'Emotion Detected',
        `I sense you're feeling ${randomEmotion} today. 🎨 Generating your Soulnote...`,
        [{ text: 'Beautiful!', style: 'default' }]
      );
    }, 1000);
  };

  const getEmotionColor = (emotion) => {
    const colorMap = {
      happy: ['#FFD700', '#FFA500'],
      sad: ['#4682B4', '#1E90FF'],
      calm: ['#98FB98', '#90EE90'],
      excited: ['#FF6347', '#FF4500'],
      thoughtful: ['#DDA0DD', '#9370DB'],
    };
    return colorMap[emotion] || ['#E6E6FA', '#D8BFD8'];
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      <LinearGradient
        colors={currentEmotion ? getEmotionColor(currentEmotion) : ['#2C1810', '#1A0E0A']}
        style={styles.gradient}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Soulnote Journal</Text>
          <Text style={styles.subtitle}>A mirror that feels</Text>
        </View>

        {/* Main Content */}
        <View style={styles.mainContent}>
          {currentEmotion ? (
            <View style={styles.emotionDisplay}>
              <Text style={styles.emotionText}>
                Today you're feeling...
              </Text>
              <Text style={styles.emotionValue}>
                {currentEmotion.toUpperCase()}
              </Text>
              <Text style={styles.emotionDescription}>
                🎨 Generating your visual diary...
              </Text>
              <Text style={styles.emotionDescription}>
                🎵 Creating your emotional soundtrack...
              </Text>
              <Text style={styles.emotionDescription}>
                ✨ Crafting your philosophical reflection...
              </Text>
            </View>
          ) : (
            <View style={styles.welcomeContent}>
              <Text style={styles.welcomeText}>
                Welcome to your emotional journey
              </Text>
              <Text style={styles.instructionText}>
                Tap the button below and share what's in your heart today
              </Text>
            </View>
          )}
        </View>

        {/* Recording Button */}
        <View style={styles.recordingSection}>
          <Animated.View
            style={[
              styles.recordButton,
              {
                transform: [
                  {
                    scale: animatedValue.interpolate({
                      inputRange: [0, 1],
                      outputRange: [1, 1.1],
                    }),
                  },
                ],
                opacity: animatedValue.interpolate({
                  inputRange: [0, 1],
                  outputRange: [1, 0.8],
                }),
              },
            ]}
          >
            <TouchableOpacity
              style={[
                styles.recordButtonInner,
                { backgroundColor: isRecording ? '#FF4444' : '#FF6B6B' }
              ]}
              onPress={handleRecordPress}
              disabled={isRecording}
            >
              <Text style={styles.recordButtonText}>
                {isRecording ? '🎤 Recording...' : '🎤 Start Recording'}
              </Text>
            </TouchableOpacity>
          </Animated.View>
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Your emotions become art, music, and wisdom
          </Text>
        </View>
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  gradient: {
    flex: 1,
  },
  header: {
    alignItems: 'center',
    paddingTop: 60,
    paddingBottom: 40,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFFFFF',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#CCCCCC',
    fontStyle: 'italic',
    textAlign: 'center',
  },
  mainContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 30,
  },
  welcomeContent: {
    alignItems: 'center',
  },
  welcomeText: {
    fontSize: 24,
    color: '#FFFFFF',
    textAlign: 'center',
    marginBottom: 20,
    fontWeight: '300',
  },
  instructionText: {
    fontSize: 16,
    color: '#CCCCCC',
    textAlign: 'center',
    lineHeight: 24,
  },
  emotionDisplay: {
    alignItems: 'center',
  },
  emotionText: {
    fontSize: 20,
    color: '#FFFFFF',
    textAlign: 'center',
    marginBottom: 10,
  },
  emotionValue: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#FFFFFF',
    textAlign: 'center',
    marginBottom: 30,
    letterSpacing: 2,
  },
  emotionDescription: {
    fontSize: 16,
    color: '#CCCCCC',
    textAlign: 'center',
    marginBottom: 10,
  },
  recordingSection: {
    alignItems: 'center',
    paddingBottom: 80,
  },
  recordButton: {
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  recordButtonInner: {
    width: 160,
    height: 160,
    borderRadius: 80,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 4,
    borderColor: '#FFFFFF',
  },
  recordButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  footer: {
    alignItems: 'center',
    paddingBottom: 30,
  },
  footerText: {
    fontSize: 14,
    color: '#999999',
    textAlign: 'center',
    fontStyle: 'italic',
  },
});
