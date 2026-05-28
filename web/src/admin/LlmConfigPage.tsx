export function LlmConfigPage() {
  return (
    <section>
      <header className="page-header">
        <h1>AI讲解</h1>
        <p>配置 OpenAI-compatible 服务后启用</p>
      </header>
      <form className="settings-form">
        <label>
          启用状态
          <select defaultValue="false">
            <option value="false">停用</option>
            <option value="true">启用</option>
          </select>
        </label>
        <label>
          Base URL
          <input placeholder="https://example.com/v1" />
        </label>
        <label>
          Model
          <input placeholder="model name" />
        </label>
        <label>
          API Key
          <input placeholder="保存后掩码显示" type="password" />
        </label>
        <button type="button">保存配置</button>
      </form>
    </section>
  );
}
