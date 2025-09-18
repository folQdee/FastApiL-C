import { useState } from "react";
import { register } from "./api";

export default function Register() {
  const [username, setUsername] = useState("");
  const [age, setAge] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    const data = await register(username, password, age);
    console.log("Register result:", data);
    alert("Регистрация успешна, теперь залогиньтесь!");
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Регистрация</h2>
      <input placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
      <input type="number" placeholder="Age" value={age} onChange={(e) => setAge(e.target.value)} />
      <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button type="submit">Зарегистрироваться</button>
    </form>
  );
}
