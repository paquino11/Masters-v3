/*
 * Copyright (c) 2020 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0
 *
 * SPDX-License-Identifier: EPL-2.0
 */
package org.eclipse.ditto.internal.utils.pubsub.api;

import java.io.NotSerializableException;
import java.util.Map;
import java.util.Objects;
import java.util.function.Predicate;
import java.util.stream.Collectors;

import org.eclipse.ditto.base.model.headers.DittoHeaders;
import org.eclipse.ditto.base.model.json.JsonParsableCommand;
import org.eclipse.ditto.base.model.json.JsonSchemaVersion;
import org.eclipse.ditto.base.model.signals.JsonParsable;
import org.eclipse.ditto.base.model.signals.SignalWithEntityId;
import org.eclipse.ditto.base.model.signals.commands.AbstractCommand;
import org.eclipse.ditto.base.model.signals.commands.Command;
import org.eclipse.ditto.json.JsonCollectors;
import org.eclipse.ditto.json.JsonFactory;
import org.eclipse.ditto.json.JsonField;
import org.eclipse.ditto.json.JsonFieldDefinition;
import org.eclipse.ditto.json.JsonObject;
import org.eclipse.ditto.json.JsonObjectBuilder;
import org.eclipse.ditto.json.JsonParseException;
import org.eclipse.ditto.json.JsonPointer;
import org.eclipse.ditto.json.JsonValue;

/**
 * Command from Publisher to Subscriber to publish a signal to local subscribers.
 */
@JsonParsableCommand(typePrefix = PublishSignal.TYPE_PREFIX, name = PublishSignal.NAME)
public final class PublishSignal extends AbstractCommand<PublishSignal> {

    /**
     * Type prefix of this command.
     */
    public static final String TYPE_PREFIX = "pubsub.command:";

    /**
     * Name of this command.
     */
    public static final String NAME = "publish";

    private static final String TYPE = TYPE_PREFIX + NAME;

    private final SignalWithEntityId<?> signal;
    private final Map<String, Integer> groups;

    private PublishSignal(final SignalWithEntityId<?> signal, final Map<String, Integer> groups) {
        super(TYPE, signal.getDittoHeaders(), Category.MODIFY);
        this.signal = signal;
        this.groups = groups;
    }

    /**
     * Create a PublishSignal command from a signal and the groups it is published to.
     *
     * @param signal the signal to publish.
     * @param groups relation between the groups where the signal is published to and the size of each group.
     * @return the command to do it.
     */
    public static PublishSignal of(final SignalWithEntityId<?> signal, final Map<String, Integer> groups) {
        return new PublishSignal(signal, groups);
    }

    /**
     * Deserialize this command.
     *
     * @param jsonObject the JSON representation of this command.
     * @param dittoHeaders the Ditto headers of the underlying signal.
     * @param parseInnerJson function to parse the inner JSON.
     * @return the deserialized command.
     */
    @SuppressWarnings("unused") // called by reflection in AnnotationBasedJsonParsable.parse
    public static PublishSignal fromJson(final JsonObject jsonObject,
            final DittoHeaders dittoHeaders,
            final JsonParsable.ParseInnerJson parseInnerJson) {

        try {
            final SignalWithEntityId<?> signal = (SignalWithEntityId<?>) parseInnerJson.parseInnerJson(
                    jsonObject.getValueOrThrow(JsonFields.SIGNAL));
            final Map<String, Integer> groups = jsonObject.getValueOrThrow(JsonFields.GROUPS)
                    .stream()
                    .collect(Collectors.toMap(JsonField::getKeyName, field -> field.getValue().asInt()));
            return new PublishSignal(signal, groups);
        } catch (final NotSerializableException e) {
            throw new JsonParseException(e.getMessage());
        }
    }

    /**
     * @return the signal to be published.
     */
    public SignalWithEntityId<?> getSignal() {
        return signal;
    }

    /**
     * Return the groups to which a signal is published, and the size of each group on the cluster level.
     * The cluster-level subscriber of each instance requires the group size in order to distribute signals
     * evenly among local subscribers.
     *
     * @return relation between the groups in which the signal is to be published and the size of each group.
     */
    public Map<String, Integer> getGroups() {
        return groups;
    }

    @Override
    protected void appendPayload(final JsonObjectBuilder jsonObjectBuilder,
            final JsonSchemaVersion schemaVersion,
            final Predicate<JsonField> predicate) {

        jsonObjectBuilder.set(JsonFields.SIGNAL, signalToJson(schemaVersion, predicate))
                .set(JsonFields.GROUPS, groups.entrySet()
                        .stream()
                        .map(entry -> JsonField.newInstance(entry.getKey(), JsonValue.of(entry.getValue())))
                        .collect(JsonCollectors.fieldsToObject()));
    }

    @Override
    public String getTypePrefix() {
        return TYPE_PREFIX;
    }

    @Override
    public Category getCategory() {
        return Category.MODIFY;
    }

    @Override
    public PublishSignal setDittoHeaders(final DittoHeaders dittoHeaders) {
        return new PublishSignal(signal.setDittoHeaders(dittoHeaders), groups);
    }

    @Override
    public JsonPointer getResourcePath() {
        return signal.getResourcePath();
    }

    @Override
    public String getResourceType() {
        return signal.getResourceType();
    }

    @Override
    public boolean equals(final Object other) {
        if (other instanceof final PublishSignal that) {
            return Objects.equals(signal, that.signal) && Objects.equals(groups, that.groups);
        } else {
            return false;
        }
    }

    @Override
    public int hashCode() {
        return Objects.hash(signal, groups);
    }

    @Override
    public String toString() {
        return getClass().getSimpleName() + "[signal=" + signal + ", groups=" + groups + "]";
    }

    private JsonObject signalToJson(final JsonSchemaVersion jsonSchemaVersion, final Predicate<JsonField> predicate) {
        final JsonObject signalJson = signal.toJson(jsonSchemaVersion, predicate);
        if (signalJson.contains(Command.JsonFields.TYPE.getPointer())) {
            return signalJson;
        } else {
            return signalJson.toBuilder().set(Command.JsonFields.TYPE, signal.getType()).build();
        }
    }

    private static final class JsonFields {

        private static final JsonFieldDefinition<JsonObject> SIGNAL =
                JsonFactory.newJsonObjectFieldDefinition("signal");

        private static final JsonFieldDefinition<JsonObject> GROUPS =
                JsonFactory.newJsonObjectFieldDefinition("groups");
    }
}
