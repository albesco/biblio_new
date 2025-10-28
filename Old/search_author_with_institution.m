function search_author_with_institution(apiKey, firstName, lastName, institution)
    % Cerca un autore su Scopus usando l'API Elsevier con nome, cognome e istituzione.
    %
    % Parametri:
    %   apiKey (string): La tua chiave API Elsevier.
    %   firstName (string): Nome dell'autore.
    %   lastName (string): Cognome dell'autore.
    %   institution (string): Nome dell'istituzione per filtrare la ricerca.

    % Base URL per l'API Scopus Author Search
    baseUrl = 'https://api.elsevier.com/content/search/author';
    
    % Costruisci la query
    query = sprintf('authlast(%s) AND authfirst(%s) AND affil(%s)', lastName, firstName, institution);
    
    % Costruisci l'URL completo con i parametri
    url = sprintf('%s?query=%s&apikey=%s&view=STANDARD', baseUrl, urlencode(query), apiKey);
    
    try
        % Effettua la richiesta HTTP GET
        options = weboptions('Timeout', 15, 'ContentType', 'json');  % Timeout e tipo di contenuto
        response = webread(url, options);  % Chiamata all'API
        
        % Mostra i risultati della ricerca
        disp('Risultati della ricerca:');
        if isfield(response, 'search-results') && isfield(response.('search-results'), 'entry')
            for i = 1:numel(response.('search-results').entry)
                entry = response.('search-results').entry{i};
                
                % Nome dell'autore
                if isfield(entry, 'preferred-name')
                    surname = entry.('preferred-name').('surname');
                    givenName = entry.('preferred-name').('given-name');
                    disp(['Nome autore: ', givenName, ' ', surname]);
                end
                
                % Affiliazione
                if isfield(entry, 'affiliation-current') && isfield(entry.('affiliation-current'), 'affiliation-name')
                    affiliation = entry.('affiliation-current').('affiliation-name');
                    disp(['Istituzione: ', affiliation]);
                end
                
                % ID autore Scopus
                if isfield(entry, 'dc:identifier')
                    authorID = entry.('dc:identifier');
                    disp(['Scopus Author ID: ', authorID]);
                end
                disp('---------------------------------------');
            end
        else
            disp('Nessun risultato trovato.');
        end
    catch ME
        % Gestione errori
        fprintf('Errore durante la chiamata API: %s\n', ME.message);
    end
end
