import { useState } from "react";
import Login from "./Login";
import Register from "./Register";
import Profile from "./Profile";

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));

  return (
    <div>
      {!token ? (
        <>
          <Login setToken={setToken} />
          <Register />
        </>
      ) : (
        <Profile token={token} />
      )}
    </div>
  );
}
