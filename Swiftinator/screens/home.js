import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, Button, ImageBackground, Modal, TouchableOpacity } from 'react-native';
import * as Haptics from 'expo-haptics';

const image = require('../assets/images/background.jpg');

const HomeScreen = () => {
    const [text, setText] = useState('');
    const [showLyrics, setShowLyrics] = useState(false);
    const [lyrics, setLyrics] = useState('');
    const [loading, setLoading] = useState(false);
    const [modalVisible, setModalVisible] = useState(false);

    const handleTextChange = (input) => {
        setText(input);
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Rigid);
    };

    const submit = async () => {
        setModalVisible(true);
        await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy, Haptics.ImpactFeedbackStyle.soft);

        const backend_url = "https://460e-2600-1017-a410-de0-88bf-bf32-8ddc-31b8.ngrok-free.app/";
        const encodedText = text.replace(/ /g, "%20");
        const url = backend_url + "get_quote" + "?query=" + encodedText;
        console.log("Sending text to backend: " + text + " with url: " + url);
        setLoading(true);
        try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setLyrics(data.lyrics);
        await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        setShowLyrics(true);
    } catch (error) {
        console.error("Error fetching data: ", error);
    } finally {
        setLoading(false);
    }
    };

    const MAX_CHAR_LIMIT = 100;

    return (
        <View style={styles.container}>
            <ImageBackground source={image} resizeMode="cover" style={styles.image}>
                <Text style={styles.text}>Swiftinator</Text>
                <View style={{ position: 'relative' }}>
                    <TextInput
                        style={[styles.input, styles.textInput, { textAlignVertical: 'top', paddingBottom: 30, color: 'white' }]}
                        value={text}
                        onChangeText={(input) => {
                            if (input.length <= MAX_CHAR_LIMIT) {
                                handleTextChange(input);
                            }
                        }}
                        placeholder="What're you feeling?"
                        placeholderTextColor={'white'}
                        maxLength={MAX_CHAR_LIMIT}
                        multiline={true}
                    />
                    <Text style={[styles.charCount, { position: 'absolute', bottom: 12, right: 15 }]}>
                        {text.length}/{MAX_CHAR_LIMIT}
                    </Text>
                </View>
                <Button
                    style={styles.submit}
                    title="Submit"
                    onPress={async () => {
                        await submit();
                    }}
                />
                <Modal
                    animationType="fade"
                    transparent={true}
                    visible={modalVisible}
                    onRequestClose={() => setModalVisible(false)}
                >
                    <View style={styles.modalOverlay}>
                        <View style={styles.modalView}>
                            <Text style={styles.modalText}>
                                {loading ? "Loading..." : showLyrics ? lyrics : "No lyrics available."}
                            </Text>
                            <TouchableOpacity
                                style={styles.closeButton}
                                onPress={() => setModalVisible(false)}
                            >
                                <Text style={styles.closeButtonText}>Close</Text>
                            </TouchableOpacity>
                        </View>
                    </View>
                </Modal>
            </ImageBackground>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#fff',
    },
    text: {
        fontSize: 20,
        fontWeight: 'bold',
        color: 'white',
    },
    input: {
        height: 90,
        margin: 12,
        borderWidth: 1,
        padding: 10,
        borderRadius: 5,
        borderColor: 'white',
    },
    textInput: {
        width: 200,
    },
    charCount: {
        color: 'gray',
    },
    submit: {
        backgroundColor: 'blue',
        padding: 10,
        borderRadius: 5,
        marginTop: 10,
        color: 'white',
    },
    image: {
        flex: 1,
        justifyContent: "center",
        width: '100%',
        alignItems: 'center',
    },
    modalOverlay: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
    },
    modalView: {
        width: '80%',
        padding: 20,
        backgroundColor: 'white',
        borderRadius: 10,
        alignItems: 'center',
        elevation: 5,
    },
    modalText: {
        fontSize: 16,
        color: '#333',
        textAlign: 'center',
        marginBottom: 20,
    },
    closeButton: {
        backgroundColor: '#2196F3',
        padding: 10,
        borderRadius: 5,
    },
    closeButtonText: {
        color: 'white',
        fontWeight: 'bold',
    },
});

export default HomeScreen;
