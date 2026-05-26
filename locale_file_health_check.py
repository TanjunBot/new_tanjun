class LocaleFileHealthCheck(HealthCheck):
    REQUIRED_KEYS = [
        "commands.help.select.placeholder",
        "commands.help.select.title",
        "commands.help.timeout.title",
        "commands.admin.addrole.missingPermission.title",
    ]
    
    @property
    def name(self) -> str: return "Locale Files"
    @property
    def critical(self) -> bool: return True  # Bot cannot communicate without translations
    
    async def run(self) -> HealthCheckResult:
        missing_files = []
        invalid_json = []
        missing_keys = []
        
        for locale in ["en", "de"]:
            filepath = f"locales/{locale}.json"
            
            # Check file exists
            if not Path(filepath).exists():
                missing_files.append(locale)
                continue
            
            # Check valid JSON
            try:
                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                invalid_json.append(f"{locale}: {e}")
                continue
            
            # Check required keys
            identifiers = {entry.get("identifier") for entry in data if isinstance(entry, dict)}
            for key in self.REQUIRED_KEYS:
                if key not in identifiers:
                    missing_keys.append(f"{locale}:{key}")
        
        issues = []
        status = HealthStatus.HEALTHY
        
        if missing_files:
            issues.append(f"Missing files: {', '.join(missing_files)}")
            status = HealthStatus.CRITICAL
        if invalid_json:
            issues.append(f"Invalid JSON: {'; '.join(invalid_json)}")
            status = HealthStatus.CRITICAL
        if missing_keys:
            issues.append(f"Missing required keys: {', '.join(missing_keys)}")
            if status != HealthStatus.CRITICAL:
                status = HealthStatus.DEGRADED
        
        if status == HealthStatus.HEALTHY:
            return HealthCheckResult(
                self.name, status,
                "Locale files are valid and contain all required keys.",
            )
        
        return HealthCheckResult(self.name, status, "; ".join(issues))