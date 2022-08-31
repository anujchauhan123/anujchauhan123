import React from "react";

import { createAppContainer, createSwitchNavigator } from "react-navigation";
import { createStackNavigator } from "react-navigation-stack";


// screens
import Login from "./src/screens/Login";
import Home from "./src/screens/Home";
import Splash from "./src/screens/Splash";
import Demo from "./src/screens/Demo";

const AuthStack = createStackNavigator(
  {
    Login: Login,
    Demo : Demo,
  },
  {
    defaultNavigationOptions: {
      headerShown: false,
    },
  }
);

const AppStack = createStackNavigator(
  {
    Home: Home,
  },
  {
    defaultNavigationOptions: {
      headerShown: false,
    },
  }
);

const AppContainer = createAppContainer(
  createSwitchNavigator(
    {
      AuthLoading: Splash,
      App: AppStack,
      Auth: AuthStack,
    },
    {
      initialRouteName: "AuthLoading",
    }
  )
);

const App = () => {
  return <AppContainer />;
};

export default App;
