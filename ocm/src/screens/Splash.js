import React, { useEffect } from "react";
import { View, Image, ActivityIndicator,StatusBar } from "react-native";
import * as SecureStore from "expo-secure-store";

const Splash = ({ navigation }) => {
  const image = "../../assets/a_CRM.png";

  useEffect(() => {
    const timer = setTimeout(() => {
      _bootstrapAsync();
    }, 2000);
    return () => {
      clearTimeout(timer);
    };
  }, []);

  const _bootstrapAsync = async () => {
    const userToken = await SecureStore.getItemAsync("sessionid");
    navigation.navigate(userToken ? "App" : "Auth");
  };
  return (
    <View
      style={{
        flex: 1,
        backgroundColor: "#84563f",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
    <StatusBar backgroundColor={"#84563f"} barStyle="light-content"></StatusBar>
      <Image source={require(image)} style={{ height: 240, width: 240 }} />
      <ActivityIndicator color="white" size="large" style={{ marginTop: 10 }} />
    </View>
  );
};

export default Splash;
