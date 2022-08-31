import React, { useState, useEffect, useRef } from "react";
import { View, ActivityIndicator, StatusBar, Platform } from "react-native";
import { WebView } from "react-native-webview";
import * as SecureStore from "expo-secure-store";
import { Overlay } from "react-native-elements";
import { TouchableOpacity, Text, BackHandler ,ImageBackground} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const Home = ({ navigation }) => {
  const [url, setUrl] = useState("");
  const [canGoBack, setCanGoBack] = useState(false)
  const [canGoForward, setCanGoForward] = useState(false)
  const [currentUrl, setCurrentUrl] = useState('')
  const [visible, setVisible] = useState(true);
  useEffect(() => {
    const values = navigation.getParam("values", "default");
    const database = navigation.getParam("database", "default");
    if (values == "default") {
      _logout();
    } else {
      let url = 'http://'+`${values.url}/web/o2b?db=${database}&login=${values.username}&password=${values.password}`;
      console.log("url************",url);
      setUrl(url);
      const timer = setTimeout(() => setVisible(false), 6000);
      return () => {
        clearTimeout(timer);
      };
    }
  }, []);

  _logout = async () => {
    await SecureStore.deleteItemAsync("sessionid");
    navigation.navigate("AuthLoading");
  };

const webviewRef = useRef(null)

  const backButtonHandler = () => {
  if (webviewRef.current) {
    webviewRef.current.goBack();
    return true; 
  }
  //return false;
}

const frontButtonHandler = () => {
  if (webviewRef.current) webviewRef.current.goForward()
}

const backHandler = BackHandler.addEventListener(
      "hardwareBackPress",
      backButtonHandler
    );


  const _onNavigationStateChange = async (webViewState) => {
    const values = navigation.getParam("values", "default");
    const url = webViewState.url.split('/web');
    console.log("url@@@@@@@@@@@@@Nirabh9999999",url)
    console.log("webViewState.url@@@@@@@@@",webViewState.url);
    const text1 = webViewState.url;
    const substring = "/web/login";
    if (webViewState.url == `${url[0]}/web/login`)  {
      //await SecureStore.deleteItemAsync("sessionid")
      //console.log("Nirabh***********@@@@@@@@@",webViewState.url);
      navigation.navigate("AuthLoading");
      let keys = ['url', 'username', 'password'];
      AsyncStorage.multiRemove(keys, (err) => {
        //console.log("keys@@@@@@@@",keys);
      });
    }
    //console.log(webViewState.url);
  };

  return (
    <View style={{ flex: 1 }}>
      {Platform.OS == "ios" ? (
        <View style={{ backgroundColor: "#84563f", height: 40 }}></View>
      ) : null}
      <StatusBar backgroundColor={"#84563f"} barStyle="light-content"></StatusBar>

      <WebView
        source={{
          uri: url,
          // uri: "https://ri-fx.erp.techtime.me",
        }}
        onNavigationStateChange={_onNavigationStateChange}
        ref={webviewRef}
      />
      <Overlay
        isVisible={visible}
        windowBackgroundColor="#84563f"
        overlayBackgroundColor="#84563f"
        width="auto"
        height="auto"
      >
        <ActivityIndicator size="large" color="white" />
      </Overlay>
      <ImageBackground source={require("../../assets/pexels-photo.jpeg")}
        style={{ height: 45,display:'none',}}>
        <View style={{
        padding: 15,
        flexDirection: 'row',
        justifyContent: 'space-around'
                }}>
      <TouchableOpacity onPress={backButtonHandler}>
        <Text style={{
                  color: 'white',
                  fontSize: 14
                }}>Back</Text>
      </TouchableOpacity>
      <TouchableOpacity onPress={frontButtonHandler}>
        <Text style={{
          color: 'white',
          fontSize: 14
        }}>Forward</Text>
      </TouchableOpacity>
    </View>
    </ImageBackground>
    </View>
  );
};

export default Home;
