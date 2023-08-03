/*
 * Copyright (c) 2021 Contributors to the Eclipse Foundation
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
package org.eclipse.ditto.internal.utils.akka;

import static org.eclipse.ditto.base.model.common.ConditionChecker.argumentNotEmpty;
import static org.eclipse.ditto.base.model.common.ConditionChecker.argumentNotNull;

import java.text.MessageFormat;
import java.util.concurrent.TimeUnit;

import javax.annotation.concurrent.NotThreadSafe;

import org.eclipse.ditto.base.model.common.ConditionChecker;
import org.junit.rules.ExternalResource;
import org.junit.runner.Description;
import org.junit.runners.model.Statement;

import com.typesafe.config.Config;
import com.typesafe.config.ConfigFactory;

import akka.actor.ActorRef;
import akka.actor.ActorSystem;
import akka.actor.Props;
import akka.stream.Materializer;
import akka.testkit.TestProbe;
import akka.testkit.javadsl.TestKit;
import scala.concurrent.duration.Duration;

/**
 * Starts an {@link ActorSystem} for the test and stops it afterwards.
 */
@NotThreadSafe
public final class ActorSystemResource extends ExternalResource {

    private final Config config;
    private String actorSystemName;
    private ActorSystem actorSystem;
    private Materializer materializer;

    private ActorSystemResource(final Config config) {
        this.config = config;
        actorSystemName = null;
        actorSystem = null;
        materializer = null;
    }

    /**
     * Returns a new instance of {@code ActorSystemResource}.
     *
     * @return the instance.
     */
    public static ActorSystemResource newInstance() {
        return new ActorSystemResource(ConfigFactory.empty());
    }

    /**
     * Returns a new instance of {@code ActorSystemResource}.
     *
     * @param config the config to be used for creating the {@code ActorSystem}.
     * @return the instance.
     * @throws NullPointerException if {@code config} is {@code null}.
     */
    public static ActorSystemResource newInstance(final Config config) {
        return new ActorSystemResource(ConditionChecker.checkNotNull(config, "config"));
    }

    @Override
    public Statement apply(final Statement base, final Description description) {
        actorSystemName = getActorSystemName(description);

        return super.apply(base, description);
    }

    private static String getActorSystemName(final Description description) {
        final String result;
        final var className = description.getTestClass().getSimpleName();
        final var methodName = description.getMethodName();
        if (null != methodName) {
            result = MessageFormat.format("{0}_{1}", className, methodName);
        } else {
            result = className;
        }

        return result;
    }

    @Override
    protected void before() throws Throwable {
        super.before();
        actorSystem = ActorSystem.create(actorSystemName, config);
    }

    public ActorSystem getActorSystem() {
        if (null == actorSystem) {
            throw new IllegalStateException("ActorSystem gets initialized only by running a test.");
        }
        return actorSystem;
    }

    public Materializer getMaterializer() {
        final Materializer result;
        if (null == materializer) {
            result = Materializer.createMaterializer(getActorSystem());
            materializer = result;
        } else {
            result = materializer;
        }

        return result;
    }

    public TestKit newTestKit() {
        return new TestKit(getActorSystem());
    }

    public TestProbe newTestProbe() {
        return new TestProbe(getActorSystem());
    }

    public TestProbe newTestProbe(final String name) {
        return new TestProbe(getActorSystem(), argumentNotNull(name, "name"));
    }

    public ActorRef newActor(final Props props) {
        final var actorSystem = getActorSystem();
        ConditionChecker.checkNotNull(props, "props");

        return actorSystem.actorOf(props);
    }

    public ActorRef newActor(final Props props, final CharSequence actorName) {
        final var actorSystem = getActorSystem();
        ConditionChecker.checkNotNull(props, "props");
        argumentNotEmpty(actorName, "actorName");

        return actorSystem.actorOf(props, actorName.toString());
    }

    public void stopActor(final ActorRef actorRef) {
        final var actorSystem = getActorSystem();
        actorSystem.stop(ConditionChecker.checkNotNull(actorRef, "actorRef"));
    }

    @Override
    protected void after() {
        TestKit.shutdownActorSystem(actorSystem, Duration.apply(5, TimeUnit.SECONDS), false);
        actorSystemName = null;
        super.after();
    }

}
